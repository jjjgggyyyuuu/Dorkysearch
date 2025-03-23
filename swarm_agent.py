import asyncio
import uuid
from typing import Dict, List, Any, Callable, Coroutine
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Task:
    id: str
    name: str
    priority: int
    status: str
    created_at: datetime
    completed_at: datetime = None
    result: Any = None
    error: str = None

class SwarmAgent:
    def __init__(self, name: str, capacity: int = 5):
        self.name = name
        self.id = str(uuid.uuid4())
        self.capacity = capacity
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.handlers: Dict[str, Callable] = {}
        
    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler for a specific task type"""
        self.handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")

    async def submit_task(self, name: str, priority: int = 1) -> str:
        """Submit a new task to the swarm"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            name=name,
            priority=priority,
            status="pending",
            created_at=datetime.now()
        )
        self.tasks[task_id] = task
        logger.info(f"Task submitted: {task_id} - {name}")
        return task_id

    async def process_task(self, task: Task):
        """Process a single task"""
        try:
            if task.name not in self.handlers:
                raise ValueError(f"No handler registered for task type: {task.name}")
            
            handler = self.handlers[task.name]
            task.status = "running"
            self.running_tasks[task.id] = task
            
            result = await handler() if asyncio.iscoroutinefunction(handler) else handler()
            
            task.result = result
            task.status = "completed"
            task.completed_at = datetime.now()
            
            self.completed_tasks[task.id] = task
            logger.info(f"Task completed: {task.id} - {task.name}")
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"Task failed: {task.id} - {task.name} - {str(e)}")
        
        finally:
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            if task.id in self.tasks:
                del self.tasks[task.id]

    async def run(self):
        """Main loop for processing tasks"""
        logger.info(f"Starting SwarmAgent: {self.name} ({self.id})")
        while True:
            if len(self.running_tasks) < self.capacity and self.tasks:
                # Sort tasks by priority
                pending_tasks = sorted(
                    self.tasks.values(),
                    key=lambda x: (-x.priority, x.created_at)
                )
                
                for task in pending_tasks:
                    if len(self.running_tasks) >= self.capacity:
                        break
                    
                    asyncio.create_task(self.process_task(task))
            
            await asyncio.sleep(0.1)

    def get_task_status(self, task_id: str) -> Dict:
        """Get the status of a specific task"""
        task = (
            self.tasks.get(task_id) or
            self.running_tasks.get(task_id) or
            self.completed_tasks.get(task_id)
        )
        
        if not task:
            return {"error": "Task not found"}
            
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "created_at": task.created_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error
        }

    def get_metrics(self) -> Dict:
        """Get current metrics of the swarm agent"""
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "capacity": self.capacity,
            "pending_tasks": len(self.tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "registered_handlers": list(self.handlers.keys())
        }

# Example usage
async def example():
    # Create a swarm agent
    agent = SwarmAgent("MainAgent", capacity=3)
    
    # Register some task handlers
    def simple_task():
        return "Task completed successfully"
    
    async def async_task():
        await asyncio.sleep(2)
        return "Async task completed"
    
    agent.register_handler("simple_task", simple_task)
    agent.register_handler("async_task", async_task)
    
    # Submit tasks
    task1_id = await agent.submit_task("simple_task", priority=1)
    task2_id = await agent.submit_task("async_task", priority=2)
    
    # Start the agent
    agent_task = asyncio.create_task(agent.run())
    
    # Wait for some time
    await asyncio.sleep(5)
    
    # Get task statuses
    print(agent.get_task_status(task1_id))
    print(agent.get_task_status(task2_id))
    
    # Get agent metrics
    print(agent.get_metrics())
    
    # Cancel the agent task
    agent_task.cancel()

if __name__ == "__main__":
    asyncio.run(example()) 