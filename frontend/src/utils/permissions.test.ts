import { describe, expect, it } from 'vitest'

import { canCreateCreditNote, canDecideCreditNote, canViewAnalytics } from './permissions'

describe('matriz de permisos de notas de crédito', () => {
  it('reserva la creación al colaborador', () => {
    expect(canCreateCreditNote('COLLABORATOR')).toBe(true)
    expect(canCreateCreditNote('DEPARTMENT_HEAD')).toBe(false)
    expect(canCreateCreditNote('ADMIN')).toBe(false)
  })

  it('reserva la decisión al jefe o administrador', () => {
    expect(canDecideCreditNote('COLLABORATOR')).toBe(false)
    expect(canDecideCreditNote('DEPARTMENT_HEAD')).toBe(true)
    expect(canDecideCreditNote('ADMIN')).toBe(true)
  })

  it('restringe la analítica al administrador', () => {
    expect(canViewAnalytics('ADMIN')).toBe(true)
    expect(canViewAnalytics('DEPARTMENT_HEAD')).toBe(false)
    expect(canViewAnalytics('COLLABORATOR')).toBe(false)
  })
})
