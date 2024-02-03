import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import Agent
from langchain_core.agents import AgentFinish
# streamlit run app.py --server.enableXsrfProtection=false

def generate_response(prompt):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.model_chat_history.append(HumanMessage(content=prompt))

    input={"input":prompt, "chat_history":st.session_state.model_chat_history}
    response=st.session_state.agent.invoke(input)

    used_tool=None
    if isinstance(response['agent_outcome'], AgentFinish):
        final_response=response["agent_outcome"].return_values["output"]

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown(final_response)
    
    else:
        final_response=response["intermediate_steps"][0][1]
        used_tool=response["intermediate_steps"][0][0].tool

    return final_response, used_tool
    
def main():

    # with st.chat_message("assistant"):  
    #     st.markdown("Incorrect date")

    st.set_page_config("Food order", page_icon="🌭")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history=[]

    if "model_chat_history" not in st.session_state:
        st.session_state.model_chat_history=[]

    if "agent" not in st.session_state:
        agent=Agent()
        st.session_state.agent=agent.get_agent()

    full_response, used_tool=None, None
    with st.sidebar:
        st.header("AI Assitant 🤖")

        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_prompt=st.text_input(label=" ", placeholder="How can I help you")
        if user_prompt:
            with st.spinner("Thinking"):
                full_response, used_tool=generate_response(user_prompt)

                if used_tool!="search_dishes":
                    st.session_state.chat_history.append({"role": "assistant", 
                                                        "content": full_response})
                
                st.session_state.model_chat_history.append(AIMessage(content=str(full_response)))
        
    if used_tool=="search_dishes":
        for res in full_response:
            st.markdown(res["item_name"])
            st.markdown(res["desription"])
            st.markdown(res["price"])
            # st.markdown(res["outlet_name"])
            # st.image(res["image"])
            st.markdown("--------------------------")
    
    # full_response


if __name__ == "__main__":
    main()


