import os, sys
import logging
from dataclasses import dataclass, field, asdict
import toml
import wandb

import torch
from lightning.pytorch import Trainer, seed_everything
from lightning.pytorch.strategies import DDPStrategy
from lightning.pytorch.loggers import WandbLogger
from lightning.pytorch.callbacks import ModelCheckpoint
from .callbacks import GitTrackerCallback
from .version import VersionManager
from .schema import validate


def lightning_run(config):
    # validate(config)  # Validate config schema    # TODO
    config.adjust()
    
    from .train_support import instantiate_model, get_data_loaders, save_results
    ## imports supporting functions from calling module / package
    
    if config.pytest:
        # config.logging.project = f"pytest-{config.logging.project}"
        config.logging.task_name = f"pytest-{config.logging.task_name}"
        config.logging.run_name = f"pytest-{config.logging.run_name}"
    
    
    # Initialize version manager, create run directory, and set up logging
    version_manager = VersionManager(config.logging.base_path)
    version_data = version_manager.load_version()
    config.logging.run_path, config.logging.run_id, config.logging.version = version_manager.new_path(config.logging.task_name, config.logging.run_name)
    run_path = config.logging.run_path
    # Initialize environment
    seed_everything(config.seed)
    
    # Save config to run directory
    config_dict = asdict(config)
    config_path = os.path.join(run_path,"config.toml")
    with open(config_path, 'w') as f:
        toml.dump(config_dict, f)
        
    logger = logging.getLogger(__name__)

    file_handler = logging.FileHandler(os.path.join(run_path, "run.log"))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
        
    # WandB setup
    wandb_logger = WandbLogger(
        project=config.logging.project,
        name=config.logging.run_name,
        notes=config.logging.notes,
        config=config_dict,
        save_dir=str(run_path)
    )
    logger.info(f"WandB initialized with project: {config.logging.project}, run name: {config.logging.run_name}")    
    
    
    if not config.pytest:
        # Save model as artifact
        call_path = sys.argv[0]
        
        artifact = wandb.Artifact(
            f"model-{config.logging.task_name}-run{config.logging.run_id}", 
            type="model-params",
            metadata={
                "task": config.logging.task_name,
                "run_path": str(run_path),
                "config": config_dict,
            }
        )
        if os.path.exists(call_path):
            artifact.add_file(call_path, name="run.py")
        artifact.save()
        logger.info(f"Parameter artifact logged: {artifact.name}")
    
    # Callbacks
    checkpoint_cb = ModelCheckpoint(
        dirpath=os.path.join(run_path,"checkpoints"),
        filename=f"{config.logging.run_id}-{{step}}",
        every_n_train_steps=config.trainer.save_freq,
        save_top_k=-1
    )
    git_cb = GitTrackerCallback()
    logger.info("Callbacks initialized: ModelCheckpoint and GitTrackerCallback")
    
    # Model initialization
    model = instantiate_model(config)
    logger.info(f"Model instantiated: {model.__class__.__name__}")
    wandb_logger.watch(model, log="all")
    
    # Data loaders
    train_loader, val_loader, test_loader = get_data_loaders(config)
    logger.info(f"Dataloaders created.")
    
    # Trainer setup
    trainer = Trainer(
        logger=wandb_logger,
        callbacks=[checkpoint_cb, git_cb],
        max_steps=config.trainer.max_steps,
        accelerator=config.trainer.accelerator,
        devices=config.trainer.devices,
        precision=config.trainer.precision,
        # strategy=config.trainer.strategy,
        # deterministic=True,
        log_every_n_steps=config.trainer.log_freq,
        val_check_interval=config.trainer.val_freq,
        limit_val_batches=config.data.val_batch_size,
    )
    logger.info(f"Trainer initialized with max steps: {config.trainer.max_steps}, devices: {config.trainer.devices}, strategy: {config.trainer.strategy}")
    
    # Training
    # if not config.test_mode:
    trainer.fit(model, train_loader, val_loader)
    logger.info("Training completed.")
    model.eval()  # Set model to evaluation mode for testing
    wandb_logger.experiment.unwatch(model)
    
    if config.pytest:
       model.asserts()
    
    # Testing and artifacts
    if trainer.is_global_zero:
        
        import jpcm.draw as draw
        
        # results = trainer.predict(model, dataloaders=test_loader)
        # logger.info(f"Testing completed with results: {results}")
        # TODO save results
        # save_results(config, results)
        # logger.info("Results saved.")
        
        ar_pred = model.ar_predict(test_loader.dataset.data, config)
        logger.info(f"Autoregressive testing completed.")
        torch.save(ar_pred, os.path.join(run_path, 'ar_pred.pt')) # btychw
        draw.mp4(os.path.join(run_path, 'autoregressive.mp4'), ar_pred[0].detach().cpu().numpy(), triplet=True) # TYCHW
            
        # if not config.pytest:
        #     # Save model as artifact
        #     artifact.add_dir("models", name="model_code")
        #     artifact.save()
        #     logger.info(f"Model artifact logged: {artifact.name}")
        
        # Finalize version info
        version_manager.finalize_run_info(run_path, config)
        
    wandb.finish()


    
