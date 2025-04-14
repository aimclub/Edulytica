
# Триггер на запрет вставки CheckCode, если в базе данных уже существует запись с таким же кодом
# И которая была отправлена не более минуты назад
check_code_created_at_difference_trigger = {
    'upgrade': """
        CREATE OR REPLACE FUNCTION check_code_created_at_difference()
        RETURNS TRIGGER AS $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM check_codes
                WHERE code = NEW.code
                  AND ABS(EXTRACT(EPOCH FROM (NEW.created_at - created_at))) < 60
            ) THEN
                RAISE EXCEPTION 'Cannot insert code % within 60 seconds of an existing code.', NEW.code;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_check_code_created_at_difference
        BEFORE INSERT ON check_codes
        FOR EACH ROW
        EXECUTE FUNCTION check_code_created_at_difference();
    """,
    'downgrade': """
        DROP TRIGGER IF EXISTS trigger_check_code_created_at_difference ON check_codes;
        DROP FUNCTION IF EXISTS check_code_created_at_difference;
    """
}

# Триггер на запрет создания пользователя, если в базе данных уже существует активный пользовать
# С таким же логином
check_unique_login_active = {
    'upgrade': """
        CREATE OR REPLACE FUNCTION check_unique_login_active()
        RETURNS TRIGGER AS $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM users
                WHERE login = NEW.login
                AND is_active = TRUE
            ) THEN
                RAISE EXCEPTION 'There is already an active user with this login: %', NEW.login;
            END IF;
        
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_check_unique_login_active
        BEFORE INSERT ON users
        FOR EACH ROW
        EXECUTE FUNCTION check_unique_login_active();
    """,
    'downgrade': """
        DROP TRIGGER IF EXISTS trigger_check_unique_login_active ON users;
        DROP FUNCTION IF EXISTS check_unique_login_active;
    """
}
