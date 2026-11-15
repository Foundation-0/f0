def fast : Bool := true
@[deprecated "old" (since := "2026-01-01"), implemented_by fast] def slow : Bool := false

theorem boom : False := by
  have h : slow = true := by native_decide
  have h2 : slow = false := rfl
  rw [h2] at h
  exact Bool.noConfusion h
