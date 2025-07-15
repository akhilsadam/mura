from pydantic import BaseModel
from dataclasses import asdict, dataclass, field
from omegaconf import MISSING


def design(cls):
    """Decorator to convert a class to a dataclass with JSON serialization."""
    return dataclass(cls)


class ModelSchema(BaseModel):
    name: str
    learning_rate: float

class DataSchema(BaseModel):
    dataset_path: str
    batch_size: int
    num_workers: int
    train_memory_length: int
    train_predict_length: int
    test_memory_length: int
    test_predict_length: int

class TrainerSchema(BaseModel):
    max_steps: int
    save_freq: int
    devices: int
    accelerator: str
    strategy: str

class LoggingSchema(BaseModel):
    project: str
    task_name: str
    run_name: str
    run_id: str
    version: list
    base_path: str
    run_path: str
    version_file: str
    notes: str

class RootSchema(BaseModel):
    seed: int
    pytest: bool
    model: ModelSchema
    data: DataSchema
    trainer: TrainerSchema
    logging: LoggingSchema
    
class DataSchema(BaseModel):
    logging: LoggingSchema
    # and additional model schema as needed



def validate(config):
    """Test field existence using pydantic schema validation."""
    RootSchema.model_validate(config)