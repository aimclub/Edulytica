import Header from "../../components/header/header"
import "./home.scss"
export const Home = ({ authorized, setAuthorized }) => {
  return (
    <div className="homePage">
      <Header authorized={authorized} setAuthorized={setAuthorized} />
      <div className="blockHome">Edulytica</div>
    </div>
  )
}
