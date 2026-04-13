from typing import List , Literal

from langchain_openrouter import ChatOpenRouter
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain.tools import tool
from langchain.agents import create_agent
from pydantic import BaseModel , Field 
import os

from dotenv import  load_dotenv

load_dotenv()


model = ChatOpenRouter(
    model="nvidia/nemotron-3-super-120b-a12b:free"
)


# Schemas
class TaskSchema(BaseModel):
    task_name:str = Field(description="task display name")
    priority: Literal["High", "Medium", "Low"] 

class TasksOut(BaseModel):
    tasks : List[TaskSchema]
    summary: str
    order : str = Field(description="example : task 1 -> task 2 -> task 3")


    



# Functions
def insight_task(tasks:List[str]) -> str:
    SYSTEM_PROMPT = SystemMessage("You are Ai Task planner your task is to summraize and Prioritize tasks based on Hardnes ")
    TaskCreator = model.with_structured_output(TasksOut)
    
    m = [SYSTEM_PROMPT, HumanMessage(f"here Tasks : \n {tasks}")]
    
    respones = TaskCreator.invoke(m)
    
    return respones
    
    
    
# Testing
if "__main__" == __name__:    
    tasks = [
    "Finish report",
    "Prepare slides",
    "Buy groceries",
    "Schedule meeting",
    "Reply to emails"
    ]
    print(insight_task(tasks))

