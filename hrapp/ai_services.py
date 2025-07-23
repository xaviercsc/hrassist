import json
import os
from django.conf import settings
from .models import JobApplication, JobPosting, CandidateProfile

try:
    import openai
    openai.api_key = settings.OPENAI_API_KEY
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AIService:
    @staticmethod
    def calculate_candidate_score(job_application):
        """Calculate AI matching score for a candidate against a job posting"""
        try:
            job = job_application.job
            candidate = job_application.candidate
            
            # Prepare candidate data
            candidate_data = {
                'total_experience': candidate.total_experience,
                'primary_skills': candidate.primary_skills,
                'education': candidate.educational_background,
                'relevant_experience': job_application.relevant_experience,
                'work_experiences': [],
                'projects': []
            }
            
            # Add work experiences
            for exp in candidate.work_experiences.all():
                candidate_data['work_experiences'].append({
                    'company': exp.company,
                    'position': exp.position,
                    'description': exp.description,
                    'duration': f"{exp.from_date} to {'Present' if exp.is_current else exp.to_date}"
                })
            
            # Add projects
            for project in candidate.projects.all():
                candidate_data['projects'].append({
                    'title': project.title,
                    'description': project.description,
                    'technologies': project.technologies
                })
            
            # Prepare job requirements
            job_requirements = {
                'title': job.title,
                'description': job.description,
                'years_of_experience': job.years_of_experience,
                'relevant_experience': job.relevant_experience,
                'key_skills': job.key_skills,
                'work_location': job.work_location
            }
            
            # Create prompt for AI scoring
            prompt = f"""
            As an AI recruiter, analyze the candidate's profile against the job requirements and provide a matching score from 1-10.
            
            Job Requirements:
            {json.dumps(job_requirements, indent=2)}
            
            Candidate Profile:
            {json.dumps(candidate_data, indent=2)}
            
            Scoring Criteria:
            - Skills match (40%)
            - Experience relevance (30%)
            - Years of experience (20%)
            - Education fit (10%)
            
            Provide only a numerical score from 1-10 as your response.
            """
            
            if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
                score = AIService._get_openai_score(prompt)
            else:
                # Fallback scoring algorithm
                score = AIService._fallback_scoring(job, candidate, job_application)
            
            # Ensure score is within range
            score = max(1, min(10, score))
            
            # Update the application with the score
            job_application.ai_score = score
            job_application.save()
            
            return score
            
        except Exception as e:
            print(f"Error calculating AI score: {e}")
            # Return a default score based on simple matching
            return AIService._fallback_scoring(job, candidate, job_application)
    
    @staticmethod
    def _get_openai_score(prompt):
        """Get score from OpenAI API"""
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            score_text = response.choices[0].message.content.strip()
            # Extract number from response
            import re
            score_match = re.search(r'\b([1-9]|10)\b', score_text)
            if score_match:
                return int(score_match.group(1))
            return 5  # Default score if parsing fails
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return 5
    
    @staticmethod
    def _fallback_scoring(job, candidate, job_application):
        """Fallback scoring algorithm when AI APIs are not available"""
        score = 0
        
        # Experience matching (40% weight)
        exp_ratio = min(candidate.total_experience / max(job.years_of_experience, 1), 1.5)
        exp_score = min(exp_ratio * 4, 4)  # Max 4 points
        score += exp_score
        
        # Skills matching (40% weight)
        job_skills = set(skill.strip().lower() for skill in job.key_skills.split(','))
        candidate_skills = set(skill.strip().lower() for skill in candidate.primary_skills.split(','))
        
        if job_skills:
            skills_match = len(job_skills.intersection(candidate_skills)) / len(job_skills)
            skills_score = skills_match * 4  # Max 4 points
            score += skills_score
        
        # Relevant experience text matching (20% weight)
        job_keywords = set(word.lower() for word in job.relevant_experience.split() if len(word) > 3)
        candidate_keywords = set(word.lower() for word in job_application.relevant_experience.split() if len(word) > 3)
        
        if job_keywords:
            keyword_match = len(job_keywords.intersection(candidate_keywords)) / len(job_keywords)
            keyword_score = keyword_match * 2  # Max 2 points
            score += keyword_score
        
        return round(score)
    
    @staticmethod
    def generate_interview_questions(job_application):
        """Generate interview questions based on job requirements and candidate profile"""
        try:
            job = job_application.job
            candidate = job_application.candidate
            
            prompt = f"""
            Generate 10 interview questions for a candidate applying for the position of {job.title}.
            
            Job Requirements:
            - Description: {job.description}
            - Required Experience: {job.years_of_experience} years
            - Key Skills: {job.key_skills}
            - Relevant Experience: {job.relevant_experience}
            
            Candidate Background:
            - Total Experience: {candidate.total_experience} years
            - Skills: {candidate.primary_skills}
            - Education: {candidate.educational_background}
            
            Please provide 10 specific, relevant interview questions that would help assess:
            1. Technical skills (4 questions)
            2. Experience relevance (3 questions)
            3. Problem-solving abilities (2 questions)
            4. Cultural fit (1 question)
            
            Format each question as a numbered list.
            """
            
            if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
                questions = AIService._get_openai_questions(prompt)
            else:
                questions = AIService._generate_fallback_questions(job, candidate)
            
            return questions
            
        except Exception as e:
            print(f"Error generating interview questions: {e}")
            return AIService._generate_fallback_questions(job, candidate)
    
    @staticmethod
    def _get_openai_questions(prompt):
        """Get interview questions from OpenAI API"""
        try:
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None
    
    @staticmethod
    def _generate_fallback_questions(job, candidate):
        """Generate fallback questions when AI APIs are not available"""
        questions = [
            f"1. Can you describe your experience with {job.key_skills.split(',')[0] if job.key_skills else 'the required technologies'}?",
            f"2. How do you see your {candidate.total_experience} years of experience fitting into this {job.title} role?",
            f"3. What specific projects have you worked on that relate to {job.title}?",
            "4. How do you approach problem-solving when faced with technical challenges?",
            f"5. Can you explain a complex technical concept related to {job.key_skills.split(',')[0] if job.key_skills else 'your field'} to a non-technical person?",
            "6. Tell me about a time when you had to learn a new technology quickly.",
            "7. How do you stay updated with the latest trends in your field?",
            "8. Describe a challenging project you've worked on and how you overcame the obstacles.",
            "9. How do you handle working under tight deadlines?",
            "10. Why are you interested in working for our company in this role?"
        ]
        
        return '\n'.join(questions)
