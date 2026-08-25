import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AuthProvider } from './auth/AuthContext'
import { AdminRoute } from './components/AdminRoute'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { RoleHome } from './components/RoleHome'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { CreditNoteDetailPage } from './pages/CreditNoteDetailPage'
import { CreditNotesPage } from './pages/CreditNotesPage'
import { LoginPage } from './pages/LoginPage'
import { NewCreditNotePage } from './pages/NewCreditNotePage'
import { OrganizationPage } from './pages/OrganizationPage'
import { PositionsPage } from './pages/PositionsPage'

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route index element={<RoleHome />} />
              <Route element={<AdminRoute />}>
                <Route path="analytics" element={<AnalyticsPage />} />
              </Route>
              <Route path="organization" element={<OrganizationPage />} />
              <Route path="positions" element={<PositionsPage />} />
              <Route path="credit-notes" element={<CreditNotesPage />} />
              <Route path="credit-notes/new" element={<NewCreditNotePage />} />
              <Route path="credit-notes/:noteId" element={<CreditNoteDetailPage />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
