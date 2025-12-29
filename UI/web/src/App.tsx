import { useRoutes } from "react-router-dom";
import routes from "./routes";
import AppHeader from "./components/app-header";

function App() {
  const element = useRoutes(routes);

  return (
    <>
      <AppHeader />
      {element}
    </>
  );
}

export default App;
