namespace MathGov

theorem step1 (n : Nat) : n + 0 = n := by
  simp

set_option linter.unnecessarySimpa false in
theorem step2 (n : Nat) : n = n + 0 := by
  simpa using (step1 n).symm

end MathGov
