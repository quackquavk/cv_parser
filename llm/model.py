from pydantic import BaseModel, Field
from typing import Optional, List
from langchain_core.output_parsers import JsonOutputParser


class WorkExperience(BaseModel):
    job_title: str = Field(description="The title of the position held")
    company_name: str = Field(description="The company where the person worked")
    start_date: str = Field(description="The start date of the position")
    end_date: Optional[str] = Field(description="The end date of the position, or 'PRESENT' if still employed")
    responsibilities: List[str] = Field(description="List of key responsibilities or accomplishments")

class Education(BaseModel):
    degree: str = Field(description="The degree or qualification obtained")
    institution: str = Field(description="The name of the school or university")
    start_date: str = Field(description="The start date of the program")
    end_date: Optional[str] = Field(description="The end date of the program, or 'PRESENT' if still studying")
    grade: Optional[str] = Field(description="The grade or honors achieved, if mentioned")

class Certification(BaseModel):
    certification_name: str = Field(description="The name of the certification")
    issuing_organization: str = Field(description="The organization that issued the certification")
    issue_date: str = Field(description="The date when the certification was issued")


class TechnicalProject(BaseModel):
    project_name: str = Field(description="The name of the technical project")
    description: str = Field(description="A brief description of the project")
    programming_language: Optional[List[str]] = Field(description="A list of the programming language used in the project")
    project_link: Optional[str] = Field(description="A link to the project repository or website [might be in alt link or plain text]")

class Scores(BaseModel):
    experience: int = Field(
        ge=1, le=250, 
        description=(
            "Score based on the years of professional experience (1-250). "
            "Points are awarded based on the total years of experience, with additional points for "
            "relevant leadership roles or specialized expertise."
        )
    )
    exp_reason: str = Field(description="Reasoning for the experience score stating why it is low or high? and what should this person do to improve it?")
    
    education: int = Field(
        ge=1, le=150, 
        description=(
            "Score based on the level and relevance of education (1-150). "
            "Higher scores for advanced degrees (Master's/PhD) and degrees in relevant fields. "
            "Additional points for certifications, continuing education, and relevant academic achievements."
        )
    )
    ed_reason: str = Field(description="Reasoning for the education score")
    
    skill: int = Field(
        ge=1, le=200, 
        description=(
            "Score based on technical skills and their relevance to the job (1-200). "
            "Higher scores for advanced proficiency in in-demand skills and technologies, "
            "and for skills that directly align with the job role."
        )
    )
    sk_reason: str = Field(description="Reasoning for the skill score stating why it is low or high? and what should this person do to improve it?")
    
    project: int = Field(
        ge=1, le=200, 
        description=(
            "Score based on the technical projects and their relevance (1-200). "
            "Points are awarded based on the complexity, impact, and leadership roles in the projects. "
            "Projects related to the job role or open-source contributions score higher."
        )
    )
    pr_reason: str = Field(description="Reasoning for the project score stating why it is low or high? and what should this person do to improve it?")
    
    presentation: int = Field(
        ge=1, le=200, 
        description=(
            "Score based on the overall presentation and completeness of the CV (1-200). "
            "Higher scores for well-organized, clear, and professional CVs. "
            "CVs tailored for the job, with no errors and a clear structure, will receive higher scores."
        )
    )
    pre_reason: str = Field(description="Reasoning for the presentation score stating why it is low or high? and what should this person do to improve it?")

#main model
class CV(BaseModel):
    name: str = Field(description="The name of the person")
    email: str = Field(description="The email of the person")
    phone_number: str = Field(description="The phone number of the person")
    address: str = Field(description="The address of the person in and strictly in the form of city, country")
    linkedin_url: Optional[str] = Field(description="The LinkedIn profile URL [might be in alt link or plain text]")
    git_url: Optional[str] = Field(description="The GitHub/ Gitlab profile URL or portfolio [might be in alt link or plain text]")
    website: Optional[str] = Field(description="The personal website URL [might be in alt link or plain text]")
    position: str = Field(description="The current position or job title of the person")
    scores: Scores = Field(description="Scores based on key criteria such as work experience, skills, qualifications, and overall presentation")
    
    all_skills: str = Field(description="Include a short details of the person[name and position] and all the skills details in short and to the point form e.g. firebase, REST API, testing debugging, leadership, communication, team_work; IFF explicitly mentioned on the CV")

    work_experience: List[WorkExperience] = Field(description="A list of the person's work experience")
    years_of_experience: float = Field(
        description=(
            "The total number of years and months of work experience, represented as a decimal number. For example, 1.2 means 1 year and 2 months.")
    )
    education: List[Education] = Field(description="A list of the person's educational qualifications")
    certifications: Optional[List[Certification]] = Field(description="A list of certifications obtained by the person")

    skills: List[str] = Field(description="A list of the person's technical and soft skills (e.g., teamwork, leadership) all in  e.g. firebase, REST API, testing debugging, leadership, communication, team_work iff explicitly mentioned anywhere in the CV")
    programming_languages: List[str] = Field(description="A list of programming languages known, used or worked on different projects and work experiences all in small letters E.g. python, java, c++, c, flutter, dart, node, django, react, vue, angular, javascript, etc if explicitly mentioned on the CV")

    technical_projects: Optional[List[TechnicalProject]] = Field(description="A list of technical projects or open-source contributions")
    research_papers: Optional[List[str]] = Field(description="A list of research papers or publications")
    languages: Optional[List[str]] = Field(description="List of languages spoken by the person and their proficiency levels")
    hobbies: Optional[List[str]] = Field(description="List of hobbies or personal interests")

    references: Optional[List[str]] = Field(description="References or contact details for referees")
    rating: int = Field(ge = 1, le = 1000, description="Rating of the provided CV based on key criteria such as work experience, skills, qualifications, and overall presentation. Rate on a scale of 1 to 1000.")


cv_parser = JsonOutputParser(pydantic_object=CV)