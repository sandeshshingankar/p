class ChatbotService:
    @staticmethod
    def get_response(question):
        import re
        q = question.lower()
        words = set(re.findall(r'[a-z]+', q))

        # 1. Greetings / Hi / Hello
        if words & {'hi', 'hello', 'hey'}:
            return "Hello! Welcome to College AI Assistant. How can I help you with your studies today?"

        # 2. Student Info / Profile
        elif 'student' in q or 'who am i' in q or 'name' in q:
            return "You are Rahul Patil, an active student enrolled in the BCA course."

        # 3. Course Info
        elif 'course' in q or 'bca' in q:
            return "Your current course is BCA (Bachelor of Computer Applications). It covers Data Structures, Computer Networks, and DBMS."

        # 4. Study Plan / Revision
        elif 'revision' in q or 'plan' in q or 'study' in q:
            return "Try a 3-block study plan: 45 mins Data Structures, 30 mins Computer Networks, followed by a 15 min break."

        # 5. Attendance
        elif 'attendance' in q:
            return "Your current overall attendance is 92%. It is in a very safe zone! Keep it up."

        # 6. Exams / Tests
        elif 'exam' in q or 'test' in q or 'paper' in q:
            return "Internal examinations start from next Monday. Please review your lab manuals and previous year question papers."

        # 7. Subject: Computer Networks
        elif 'network' in q or 'dcn' in q:
            return "For Computer Networks (DCN), focus heavily on OSI layers, IP addressing, and TCP/UDP handshake protocols."

        # 8. Subject: Python
        elif 'python' in q:
            return "In Python, focus on Object-Oriented Programming (OOP), exception handling, and database connectivity with SQLite."

        # 9. Subject: Java
        elif 'java' in q:
            return "In Java, make sure you clear your concepts on Exception Handling, Multithreading, and Collections Framework."

        # 10. Subject: DBMS / SQL
        elif 'dbms' in q or 'sql' in q:
            return "For DBMS, practice writing complex SQL queries involving JOINs, GROUP BY, subqueries, and database normalization."

        # Default Fallback Response
        return "I am your AI study assistant. You can ask me about study plans, attendance, course details, exams, or specific subjects like Python, Java, and DBMS!"