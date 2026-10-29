from datetime import datetime
from models import (
    db, Recommendation, Category, TestAttempt, AttemptAnswer,
    Question, CodingProblem, CodingSubmission, HRPractice, HRQuestion
)

def calculate_student_category_performances(user_id: int):
    """
    Computes accurate percentage performance for a student across all categories,
    coding practice, and HR preparation.
    Returns: dict { 'category_name': {'score': float, 'attempts': int, 'category_id': int}, ... }
    """
    categories = Category.query.all()
    results = {}

    for cat in categories:
        # Check test attempts questions belonging to this category
        answers = db.session.query(AttemptAnswer)\
            .join(TestAttempt, AttemptAnswer.attempt_id == TestAttempt.id)\
            .join(Question, AttemptAnswer.question_id == Question.id)\
            .filter(TestAttempt.user_id == user_id, Question.category_id == cat.id)\
            .all()

        total_ans = len(answers)
        if total_ans > 0:
            correct_ans = sum(1 for a in answers if a.is_correct)
            score = round((correct_ans / total_ans) * 100, 1)
            results[cat.name] = {
                'score': score,
                'attempts': total_ans,
                'category_id': cat.id
            }

    # Evaluate Coding performance
    total_problems = CodingProblem.query.count()
    if total_problems > 0:
        solved_count = db.session.query(CodingSubmission.problem_id)\
            .filter(CodingSubmission.user_id == user_id, CodingSubmission.result_status == 'Accepted')\
            .distinct().count()
        coding_attempts = CodingSubmission.query.filter_by(user_id=user_id).count()
        if coding_attempts > 0:
            coding_score = round((solved_count / total_problems) * 100, 1)
            results['Coding Practice'] = {
                'score': coding_score,
                'attempts': coding_attempts,
                'category_id': None
            }

    # Evaluate HR practice performance
    total_hr_q = HRQuestion.query.count()
    if total_hr_q > 0:
        practiced_hr = HRPractice.query.filter_by(user_id=user_id, is_practiced=True).count()
        if practiced_hr > 0:
            hr_score = round((practiced_hr / total_hr_q) * 100, 1)
            results['HR Interview'] = {
                'score': hr_score,
                'attempts': practiced_hr,
                'category_id': None
            }

    return results

def generate_recommendations(user_id: int):
    """
    Evaluates student performance using rule-based criteria and generates
    smart personalized recommendations stored in the database.
    """
    performances = calculate_student_category_performances(user_id)

    # Remove incomplete recommendations that are older or superseded
    Recommendation.query.filter_by(user_id=user_id, is_completed=False).delete()

    generated_recommendations = []

    # Case A: Onboarding / Cold Start (No recorded performance data)
    if not performances:
        onboarding_rules = [
            {
                'title': "Take Your Diagnostic Mock Test",
                'priority': "High",
                'explanation': "You haven't attempted any timed mock tests yet. A diagnostic test establishes your baseline score across technical and aptitude areas.",
                'suggested_action': "Start with the Campus Placement Diagnostic Mock Test to identify your strengths and weaknesses.",
                'target_url': "/mock-tests",
                'category_id': None
            },
            {
                'title': "Explore Core Technical Questions",
                'priority': "Moderate",
                'explanation': "Review curated conceptual and technical questions in Java, Python, DBMS, and Operating Systems.",
                'suggested_action': "Browse through the Question Bank and bookmark essential topics.",
                'target_url': "/questions",
                'category_id': None
            },
            {
                'title': "Kickstart Python Coding Practice",
                'priority': "Moderate",
                'explanation': "Hands-on coding is heavily weighted in technical placement rounds.",
                'suggested_action': "Solve beginner programming problems starting with Array and String manipulation.",
                'target_url': "/coding",
                'category_id': None
            },
            {
                'title': "Prepare Your HR Introduction",
                'priority': "Steady",
                'explanation': "HR interviews require confident communication using structured responses like the STAR method.",
                'suggested_action': "Draft your answer to 'Tell me about yourself' in the HR Preparation module.",
                'target_url': "/hr-practice",
                'category_id': None
            }
        ]
        for rule in onboarding_rules:
            rec = Recommendation(
                user_id=user_id,
                title=rule['title'],
                priority=rule['priority'],
                explanation=rule['explanation'],
                suggested_action=rule['suggested_action'],
                target_url=rule['target_url'],
                category_id=rule['category_id'],
                is_completed=False,
                created_at=datetime.utcnow()
            )
            db.session.add(rec)
            generated_recommendations.append(rec)
        db.session.commit()
        return generated_recommendations

    # Case B: Performance-driven rule engine
    # Sort categories by score ascending (lowest score gets highest priority)
    sorted_items = sorted(performances.items(), key=lambda x: x[1]['score'])

    for name, data in sorted_items:
        score = data['score']
        cat_id = data['category_id']

        # Rule 1: Below 50% -> High-Priority Revision
        if score < 50.0:
            priority = "High"
            if name == 'Coding Practice':
                title = f"Prioritize Coding Practice (Current: {score}%)"
                explanation = f"Your coding score of {score}% is below the 50% threshold. Technical interviewers place heavy emphasis on practical problem solving."
                suggested_action = "Review array, string, and math problems. Solve at least 3 beginner problems today."
                url = "/coding"
            elif name == 'HR Interview':
                title = f"Accelerate HR Preparation (Current: {score}%)"
                explanation = f"Your HR completion is at {score}%. Behavioral questions determine cultural fit and final selection."
                suggested_action = "Practice standard questions such as strengths, weaknesses, and teamwork using the STAR framework."
                url = "/hr-practice"
            else:
                title = f"Urgent Revision: {name} (Current: {score}%)"
                explanation = f"Your accuracy in {name} is currently {score}%, which is below the recommended 50% placement benchmark."
                suggested_action = f"Revise {name} fundamentals in the Question Bank and retake topic assessments."
                url = f"/questions?category={cat_id}" if cat_id else "/questions"

        # Rule 2: 50% to 69% -> Moderate Practice Required
        elif 50.0 <= score < 70.0:
            priority = "Moderate"
            if name == 'Coding Practice':
                title = f"Strengthen Algorithm Techniques (Current: {score}%)"
                explanation = f"You have solved {score}% of coding challenges. Improving to 70%+ ensures readiness for coding rounds."
                suggested_action = "Tackle medium difficulty problems on searching, sorting, and frequency counting."
                url = "/coding"
            elif name == 'HR Interview':
                title = f"Refine HR Scenarios (Current: {score}%)"
                explanation = f"Your HR readiness is at {score}%. Focus on situational and conflict resolution questions."
                suggested_action = "Write out personal examples for handling pressure and workplace challenges."
                url = "/hr-practice"
            else:
                title = f"Practice Core {name} Topics (Current: {score}%)"
                explanation = f"Your score in {name} is {score}%. You have solid foundational knowledge but need targeted practice on tricky concepts."
                suggested_action = f"Practice medium-level {name} questions and review detailed explanations."
                url = f"/questions?category={cat_id}" if cat_id else "/questions"

        # Rule 3: 70% to 84% -> Continue Practice and Revise Weak Topics
        elif 70.0 <= score < 85.0:
            priority = "Steady"
            if name == 'Coding Practice':
                title = f"Solid Coding Momentum (Current: {score}%)"
                explanation = f"Great work reaching {score}% coding proficiency. Work on code optimization and edge cases."
                suggested_action = "Solve remaining challenging problems and verify time/space constraints."
                url = "/coding"
            else:
                title = f"Solid Progress in {name} (Current: {score}%)"
                explanation = f"You are demonstrating good proficiency in {name} with a {score}% score. Keep the momentum going!"
                suggested_action = f"Take full-length mock tests to test your speed and accuracy under time pressure."
                url = "/mock-tests"

        # Rule 4: 85% or higher -> Maintain Proficiency & Advanced Challenges
        else:
            priority = "Advanced"
            title = f"Mastery Achieved in {name} (Current: {score}%)"
            explanation = f"Excellent! You have achieved {score}% proficiency in {name}, putting you in the top tier."
            suggested_action = f"Maintain your proficiency with rapid revision and help peers or tackle hard problems."
            url = f"/questions?category={cat_id}" if cat_id else "/questions"

        rec = Recommendation(
            user_id=user_id,
            category_id=cat_id,
            title=title,
            priority=priority,
            explanation=explanation,
            suggested_action=suggested_action,
            target_url=url,
            is_completed=False,
            created_at=datetime.utcnow()
        )
        db.session.add(rec)
        generated_recommendations.append(rec)

    db.session.commit()
    return generated_recommendations
