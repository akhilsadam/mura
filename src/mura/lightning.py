
from lightning.pytorch import Trainer, seed_everything
from lightning.pytorch.strategies import DDPStrategy
from lightning.pytorch.loggers import WandbLogger
from lightning.pytorch.callbacks import ModelCheckpoint
from .callbacks import GitTrackerCallback
from .version import VersionManager
from .train_support import *
from .schema import validate

def lightning_run(config: DictConfig):
    validate(config)  # Validate config schema    
    
    if config.pytest:
        config.logging.project = f"pytest-{config.logging.project}"
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
    config_path = os.path.join(run_path,"config.yaml")
    OmegaConf.save(config, config_path)        # TODO fix
        
    # WandB setup
    wandb_logger = WandbLogger(
        project=config.logging.project,
        name=config.logging.run_name,
        notes=config.logging.notes,
        config=asdict(config),
        save_dir=str(run_path)
    )
    logger.info(f"WandB initialized with project: {config.logging.project}, run name: {config.logging.run_name}")    
    
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
        # strategy=config.trainer.strategy,
        # deterministic=True,
        log_every_n_steps=50
    )
    logger.info(f"Trainer initialized with max steps: {config.trainer.max_steps}, devices: {config.trainer.devices}, strategy: {config.trainer.strategy}")
    
    # Training
    # if not config.test_mode:
    trainer.fit(model, train_loader, val_loader)
    logger.info("Training completed.")
    model.eval()  # Set model to evaluation mode for testing
    
    if config.pytest:
       model.asserts()
    
    # Testing and artifacts
    if trainer.is_global_zero:
        results = trainer.predict(model, dataloaders=test_loader)
        logger.info(f"Testing completed with results: {results}")
        # TODO save results
        save_results(config, results)
        logger.info("Results saved.")
            
        if not config.pytest:
            # Save model as artifact
            artifact = wandb_logger.experiment.Artifact(
                f"model-{config.logging.task_name}-run{config.logging.run_id}", 
                type="model",
                metadata={
                    "task": config.logging.task_name,
                    "run_path": str(run_path),
                    "config": OmegaConf.to_container(config, resolve=True)
                }
            )
            artifact.add_file(os.path.join(run_path,"checkpoints"))
            wandb_logger.experiment.log_artifact(artifact)
            logger.info(f"Model artifact logged: {artifact.name}")
        
        # Finalize version info
        version_manager.finalize_run_info(run_path, config)
        
    wandb.finish()
