import { useNavigate } from "react-router-dom";
import { useAuth } from "../provider/authProvider";
import instance from "../provider/jwtInterceptor"

const Logout = (props) => {
    const { clearToken } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        instance.get(
            props.url, { withCredentials: true, }
        )
            .then(response => {
            })
            .catch(error => console.error(error));
        clearToken()
        navigate("/", { replace: true });
    };
    handleLogout();
};

export default Logout;