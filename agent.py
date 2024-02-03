from langchain import hub
import os
os.environ["OPENAI_API_KEY"] = "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"
from langchain.agents import create_openai_functions_agent
from langchain_openai.chat_models import ChatOpenAI
from typing import TypedDict, Annotated, List, Union
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
import operator
from langchain_core.agents import AgentFinish
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.graph import END, StateGraph
from tools import search_dishes, place_order


class AgentState(TypedDict):
   input: str
   chat_history: list[BaseMessage]
   agent_outcome: Union[AgentAction, AgentFinish, None]
   intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]

class Agent():
    def __init__(self) -> None:
        tools = [search_dishes,place_order]
        prompt = hub.pull("hwchase17/openai-functions-agent")
        llm = ChatOpenAI(model="gpt-3.5-turbo-1106", streaming=True)
        self.agent_runnable = create_openai_functions_agent(llm, tools, prompt)
        self.tool_executor = ToolExecutor(tools)
    
    def run_agent(self,data):
        agent_outcome = self.agent_runnable.invoke(data)
        return {"agent_outcome": agent_outcome}
    
    def execute_tools(self,data):
        agent_action = data['agent_outcome']
        # response = input(prompt=f"[y/n] continue with: {agent_action}?")
        # if response == "n":
        #     raise ValueError
        # print(f"------------{agent_action}---------------")
        output = self.tool_executor.invoke(agent_action)
        return {"intermediate_steps": [(agent_action,output)]}
        
    def should_continue(self,data):
        if isinstance(data['agent_outcome'], AgentFinish):
            return "end"
        else:
            if data["agent_outcome"].tool=="search_dishes":
              return "final"
            
            return "continue"
    
    def get_agent(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", self.run_agent)
        workflow.add_node("action", self.execute_tools)
        workflow.add_node("final", self.execute_tools)

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            start_key="agent",
            condition=self.should_continue,
            conditional_edge_mapping={
                "continue":"action",
                "final": "final",
                "end":END
            }
        )

        workflow.add_edge('action', 'agent')
        workflow.add_edge('final', END)

        agent = workflow.compile()

        return agent
