import { BrowserRouter, Route, Routes } from "react-router-dom"
import { Shell } from "./components/Shell"
import { CreateProject } from "./pages/CreateProject"
import { Dashboard } from "./pages/Dashboard"
import { EditorPage } from "./pages/EditorPage"
import { LibraryPage } from "./pages/LibraryPage"
import { ProjectPage } from "./pages/ProjectPage"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Shell />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/new" element={<CreateProject />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/projects/:projectId" element={<ProjectPage />} />
          <Route path="/projects/:projectId/editor/:generationId" element={<EditorPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
