export type UserRole = 'ADMIN' | 'DEPARTMENT_HEAD' | 'COLLABORATOR'
export type CreditNoteStatus = 'PENDING' | 'APPROVED' | 'REJECTED'
export type CreditNoteAction = 'CREATED' | 'APPROVED' | 'REJECTED'
export type Currency = 'USD' | 'VES'
export type EmployeeStatus = 'ACTIVE' | 'INACTIVE'
export type Seniority = 'ASSISTANT' | 'JUNIOR' | 'SEMI_SENIOR' | 'SENIOR' | 'LEAD'

export interface CurrentUser {
  id: number
  username: string
  role: UserRole
  employee_id: number
  full_name: string
  internal_email: string
  department_id: number
  department_name: string
}

export interface Department {
  id: number
  code: string
  name: string
  description: string | null
}

export interface BusinessFunction {
  id: number
  code: string
  name: string
  description: string | null
}

export interface Position {
  id: number
  title: string
  seniority: Seniority
  department: Department
  functions: BusinessFunction[]
}

export interface EmployeeDirectoryItem {
  id: number
  full_name: string
  position_title: string
  seniority: Seniority
  department_name: string
  status: EmployeeStatus
}

export interface EmployeeDetail extends EmployeeDirectoryItem {
  country: string
  hire_date: string
  internal_email: string
}

export interface CatalogItem {
  id: number
  name: string
}

export interface CreditNoteEvent {
  id: number
  action: CreditNoteAction
  previous_status: CreditNoteStatus | null
  new_status: CreditNoteStatus
  comment: string | null
  actor_id: number
  actor_username: string
  actor_role: UserRole
  occurred_at: string
}

export interface CreditNote {
  id: number
  amount: string
  currency: Currency
  reason: string
  status: CreditNoteStatus
  version: number
  requesting_department: Department
  creator_id: number
  creator_username: string
  store: CatalogItem
  company: CatalogItem
  created_at: string
  updated_at: string
  events: CreditNoteEvent[]
}

export interface CreditNoteList {
  items: CreditNote[]
  total: number
  limit: number
  offset: number
}

export interface CreditNoteCatalog {
  stores: CatalogItem[]
  companies: CatalogItem[]
}

