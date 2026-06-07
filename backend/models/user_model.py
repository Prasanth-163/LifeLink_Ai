from database.db import get_db_connection


class UserModel:

    @staticmethod
    def get_user_by_email(email):

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        return user