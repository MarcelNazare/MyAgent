from typing import List, Literal, Dict, Optional
from agency_swarm import Agent, Agency, set_openai_key, BaseTool
from pydantic import Field, BaseModel
import streamlit as st

class AnalyzeProjectRequirements(BaseTool):
    project_name: str = Field(..., description="Name of the project")
    project_description: str = Field(..., description="Project description and goals")
    budget_range: Literal["$120-$299", "$299-$499", "$499-$999", "$1k+"] = Field(..., 
                         description="Budget range for the project")

    class ToolConfig:
        name = "analyze_project"
        description = "Analyzes project requirements and feasibility"
        one_call_at_a_time = True

    def run(self) -> str:
        """Analyzes project and stores results in shared state"""
        if self._shared_state.get("project_analysis", None) is not None:
            raise ValueError("Project analysis already exists.")
        
        analysis = {
            "name": self.project_name,
            #"type": self.project_type,
            "complexity": "high",
            "timeline": "2 months",
            "budget_feasibility": "within range",
            "requirements": ["Industry Research","Market and Competitor Research","Brand Strategy Research", "Marketing Strategy Research","Social Media Competitor Research", "Content Creation Research"]
        }
        
        self._shared_state.set("project_analysis", analysis)
        return "Project analysis completed."

def init_session_state() -> None:
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None

    

def main() -> None:
    st.set_page_config(page_title="Wona Design Studio", layout="wide")
    init_session_state()
    
    st.title("Wona Design Studio")
    
    # API Configuration
    with st.sidebar:
        st.header("🔑 API Configuration")
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to continue"
        )

        if openai_api_key:
            st.session_state.api_key = openai_api_key
            st.success("API Key accepted!")
        else:
            st.warning("⚠️ Please enter your OpenAI API Key to proceed")
            st.markdown("[Get your API key here](https://platform.openai.com/api-keys)")
            return
        
    # Initialize agents with the provided API key
    set_openai_key(st.session_state.api_key)
    api_headers = {"Authorization": f"Bearer {st.session_state.api_key}"}
    
    # Project Input Form
    with st.form("project_form"):
        st.subheader("Project Details")
        
        project_name = st.text_input("Project Name")
        project_description = st.text_area(
            "Project Description",
            help="Describe the project, its goals, and any specific requirements"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            timeline = st.selectbox(
                "Expected Timeline",
                ["1-2 months", "3-4 months", "5-6 months", "6+ months"]
            )
        with col2:
            budget_range = st.selectbox(
                "Budget Range",
                ["$120-$299", "$299-$499", "$499-$999", "$1k+"]
            )
            priority = st.selectbox(
                "Project Priority",
                ["High", "Medium", "Low"]
            )
        
        special_considerations = st.text_area(
            "Special Considerations (optional)",
            help="Any additional information or special requirements"
        )
        
        submitted = st.form_submit_button("Analyze Project")
        
        if submitted and project_name and project_description:
            try:
                # Set OpenAI key
                set_openai_key(st.session_state.api_key)
                
                # Create agents
                ### Project Analyst
                project_analyst = Agent(
                    name="Project Analyst",
                    description="You are Project Analyst with a lot of experience in evaluating projects and making strategic decisions in creative design and marketing industry.",
                    instructions="""
                    You are an experienced Creative Project Analyst who evaluates projects. Follow these steps strictly:

                    1. FIRST, use the AnalyzeProjectRequirements tool with:
                       - project_name: The name from the project details
                       - project_description: The full project description
                       - budget_range: The specified budget range

                    2. WAIT for the analysis to complete before proceeding.
                    
                    3. Review the analysis results and provide strategic recommendations.
                    """,
                    tools=[AnalyzeProjectRequirements],
                    api_headers=api_headers,
                    temperature=0.7,
                    max_prompt_tokens=25000
                )
                ### Brand Strategist
                brand_strategist = Agent(
                    name="Seasoned Brand Strategist",
                    description="You are a seasoned brand stratgist who specialises in brand strategy creation.",
                    instructions="""
                    You are a marketing expert. Follow these steps strictly:

                    1. WAIT for the project analysis to be completed by the Project Analyst.
                    
                    2. Use your experience a Brand Strategist and follow the template below:
                       

                    3. Review and provide additional recommendations.
                    """,
                    
                    api_headers=api_headers,
                    temperature=0.7,
                    max_prompt_tokens=25000
                )                
                ### Marketing Strategist
                marketing_strategist = Agent(
                    name="Marketing Strategy Expert",
                    description="Senior Marketing Expert who specialises in Marketing.",
                    instructions="""
                    You are a marketing expert. Follow these steps strictly:

                    1. WAIT for the project analysis to be completed by the Project Analyst.
                    
                    2. Use your experience a Marketing Expert and follow the template below:
                       Conduct thorough market research to identify industry trends, opportunities, and challenges.
                       Analyze competitors to understand positioning and differentiation.
                       Define target audiences and develop detailed buyer personas.

                    3. Review and provide additional recommendations.
                    4. Lastly create a well detailed Markerting Strategy
                    """,
                    
                    api_headers=api_headers,
                    temperature=0.7,
                    max_prompt_tokens=25000
                )
                ### Sales Strategist
                sales_strategist = Agent(
                    name="Sales Strategy Expert",
                    description="Senior Marketing Expert who specialises in Marketing.",
                    instructions="""
                    You are a marketing expert. Follow these steps strictly:

                    1. WAIT for the project analysis to be completed by the CEO.
                    
                    2. Use your experience a Marketing Expert and follow the template below:
                       #template

                    3. Review and provide additional recommendations.
                    """,
                    
                    api_headers=api_headers,
                    temperature=0.7,
                    max_prompt_tokens=25000
                )

                # Create agency
                agency = Agency(
                    [
                        project_analyst, brand_strategist,marketing_strategist,sales_strategist, 
                        [project_analyst,brand_strategist],
                        [project_analyst, marketing_strategist],
                        [project_analyst, sales_strategist]
                  
                    ],
                    async_mode='threading',
                    shared_files='shared_files'
                )
                
                # Prepare project info
                project_info = {
                    "name": project_name,
                    "description": project_description,
                    "timeline": timeline,
                    "budget": budget_range,
                    "priority": priority,
                    "special_considerations": special_considerations
                }

                st.session_state.messages.append({"role": "user", "content": str(project_info)})
                # Create tabs and run analysis
                with st.spinner("AI Services Agency is analyzing your project..."):
                    try:
                        # Get analysis from each agent using agency.get_completion()
                        project_analyst_response = agency.get_completion(
                            message=f"""Analyze this project using the AnalyzeProjectRequirements tool:
                            Project Name: {project_name}
                            Project Description: {project_description}
                            Budget Range: {budget_range}
                            
                            Use these exact values with the tool and wait for the analysis results.""",
                            recipient_agent=project_analyst
                        )
                        
                        brand_strategist_response = agency.get_completion(
                            message=f"""Review the project analysis and create technical specifications using the CreateTechnicalSpecification tool.
                            Choose the most appropriate:
                            - architecture_type (monolithic/microservices/serverless/hybrid)
                            - core_technologies (comma-separated list)
                            - scalability_requirements (high/medium/low)
                            
                            Base your choices on the project requirements and analysis.""",
                            recipient_agent=brand_strategist
                        )
                        
                        sales_strategist_response = agency.get_completion(
                            message=f"Analyze project management aspects: {str(project_info)}",
                            recipient_agent=sales_strategist,
                            additional_instructions="Focus on product-market fit and roadmap development, and coordinate with technical and marketing teams."
                        )

                        marketing_strategist_response = agency.get_completion(
                            message=f"Analyze project management aspects: {str(project_info)}",
                            recipient_agent=marketing_strategist,
                            additional_instructions="Focus on product-market fit and roadmap development, and coordinate with technical and marketing teams."
                        )
                        
                        # Create tabs for different analyses
                        tabs = st.tabs([
                            "Project Analyst's Project Analysis",
                            "Brand Strategist Brand Stragy",
                            "Marketing Strategists Marketing Strategy",
                            "Sales Strategists Sales Strategy"
                          
                        ])
                        
                        with tabs[0]:
                            st.markdown("## Project Analyst's Project Analysis")
                            st.markdown(project_analyst_response)
                            st.session_state.messages.append({"role": "assistant", "content": project_analyst_response})
                        
                        with tabs[1]:
                            st.markdown("## Brand Strategist Brand Stragy")
                            st.markdown(brand_strategist_response)
                            st.session_state.messages.append({"role": "assistant", "content": brand_strategist_response})
                        
                        with tabs[2]:
                            st.markdown("## Marketing Strategists Marketing Strategy")
                            st.markdown(marketing_strategist_response)
                            st.session_state.messages.append({"role": "assistant", "content": marketing_strategist_response})
                        
                        with tabs[3]:
                            st.markdown("## Sales Strategists Sales Strategy")
                            st.markdown(sales_strategist_response)
                            st.session_state.messages.append({"role": "assistant", "content": sales_strategist_response})
 

                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
                        st.error("Please check your inputs and API key and try again.")

            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.error("Please check your API key and try again.")

    # Add history management in sidebar
    with st.sidebar:
        st.subheader("Options")
        if st.checkbox("Show Analysis History"):
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        if st.button("Clear History"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()