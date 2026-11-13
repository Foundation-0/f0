/-
  deep-fields/scouting/acq-reference/AnchoredConservationQuotient.lean
  Zero-dependency stock Lean 4 (`Init`) formal verification suite for the
  Four-Gate Anchored Conservation Quotient (ACQ) architecture.

  Compiles in stock Lean 4 `Init` with zero external libraries, zero `sorry`,
  zero extra axioms, zero `ac_rfl`, zero `simp`, and strictly linear `omega`.
-/

namespace Foundation0.ACQ

private theorem sub_one_mul (r p : Int) :
    (r - 1) * p = r * p - p :=
  calc
    (r - 1) * p = r * p - 1 * p := Int.sub_mul r 1 p
    _ = r * p - p := congrArg (fun t => r * p - t) (Int.one_mul p)

private theorem mul_swap_outer (A D B : Int) :
    (A * D) * B = (D * B) * A :=
  calc
    (A * D) * B = B * (A * D) := Int.mul_comm (A * D) B
    _ = B * (D * A) := congrArg (fun t => B * t) (Int.mul_comm A D)
    _ = (B * D) * A := (Int.mul_assoc B D A).symm
    _ = (D * B) * A := congrArg (fun t => t * A) (Int.mul_comm B D)

private theorem lin_den (RP p : Int) :
    RP + (1 - p) = (RP - p) + 1 := by
  omega

private theorem lin_pgl2 (RP CRP CP c : Int) :
    (RP - CRP) + ((CRP - CP) + c) = (RP - CP) + c := by
  omega

theorem pgl2_bleed_isomorphism (p r c : Int) :
    (1 - c) * (r * p) + c * ((r - 1) * p + 1) = (r - c) * p + c := by
  have h1 : (1 - c) * (r * p) = r * p - (c * r) * p := by
    calc
      (1 - c) * (r * p) = 1 * (r * p) - c * (r * p) := Int.sub_mul 1 c (r * p)
      _ = r * p - c * (r * p) := by rw [Int.one_mul (r * p)]
      _ = r * p - (c * r) * p := by rw [← Int.mul_assoc c r p]
  have h2 : c * ((r - 1) * p + 1) = ((c * r) * p - c * p) + c := by
    calc
      c * ((r - 1) * p + 1) = c * ((r - 1) * p) + c * 1 := Int.mul_add c ((r - 1) * p) 1
      _ = c * (r * p - p) + c := by rw [sub_one_mul r p, Int.mul_one c]
      _ = (c * (r * p) - c * p) + c := by rw [Int.mul_sub c (r * p) p]
      _ = ((c * r) * p - c * p) + c := by rw [← Int.mul_assoc c r p]
  have h3 : (r - c) * p + c = (r * p - c * p) + c := by
    rw [Int.sub_mul r c p]
  rw [h1, h2, h3]
  exact lin_pgl2 (r * p) ((c * r) * p) (c * p) c

theorem within_shard_shift_invariant (sPos sNeg delta : Int) :
    (sPos + delta > sNeg + delta) ↔ (sPos > sNeg) := by
  omega

theorem cross_shard_shift_inversion :
    ∃ (sPos sNeg deltaPos deltaNeg : Int),
      sPos > sNeg ∧ ¬ (sPos + deltaPos > sNeg + deltaNeg) := by
  exact ⟨10, 5, 0, 6, by decide, by decide⟩

inductive AdmissiblePath (h : Nat → Int) : Nat → Int → Prop where
  | goal {g : Nat} (hz : h g = 0) : AdmissiblePath h g 0
  | step {u v : Nat} {cost remCost : Int}
      (hadm : h u ≤ cost + h v)
      (hrest : AdmissiblePath h v remCost) :
      AdmissiblePath h u (cost + remCost)

theorem quotient_path_lower_bound {h : Nat → Int} {s : Nat} {total : Int}
    (hp : AdmissiblePath h s total) :
    h s ≤ total := by
  induction hp with
  | goal hz => omega
  | step hadm _ ih => omega

inductive ValidExecution : Nat → Nat → Prop where
  | halt (b : Nat) : ValidExecution b 0
  | step {b b' k : Nat} (h_pos : 0 < b) (h_monotone : b' < b)
      (h_rest : ValidExecution b' k) : ValidExecution b (k + 1)

theorem strict_ordinal_termination {b k : Nat} (h : ValidExecution b k) : k ≤ b := by
  induction h with
  | halt b => exact Nat.zero_le b
  | @step b b' k _ h_mono _ ih => omega

theorem survival_ratio_linearization (p r c : Int) :
    (1 - p) * (r * p + (1 - p)) * (1 - c) =
      ((r - 1) * p + 1) * ((1 - c) * (1 - p)) := by
  have hden : r * p + (1 - p) = (r - 1) * p + 1 := by
    rw [sub_one_mul r p]
    exact lin_den (r * p) p
  calc
    ((1 - p) * (r * p + (1 - p))) * (1 - c)
      = ((1 - p) * ((r - 1) * p + 1)) * (1 - c) := by rw [hden]
    _ = (((r - 1) * p + 1) * (1 - c)) * (1 - p) :=
          mul_swap_outer (1 - p) ((r - 1) * p + 1) (1 - c)
    _ = ((r - 1) * p + 1) * ((1 - c) * (1 - p)) :=
          Int.mul_assoc ((r - 1) * p + 1) (1 - c) (1 - p)

def mitosisTriggered
    (err errFloor gradPar parCeil gradOrth orthFloor mdrNum mdrDen : Int) : Prop :=
  err > errFloor ∧
  gradPar ≤ parCeil ∧
  orthFloor ≤ gradOrth ∧
  gradOrth * mdrDen ≥ mdrNum * gradPar

theorem subfloor_dust_never_triggers_mitosis
    (err errFloor gradPar parCeil gradOrth orthFloor mdrNum mdrDen : Int)
    (h_dust : gradOrth < orthFloor) :
    ¬ mitosisTriggered err errFloor gradPar parCeil gradOrth orthFloor mdrNum mdrDen := by
  intro h
  rcases h with ⟨_, _, h_floor, _⟩
  omega

theorem cross_domain_rational_witnesses :
    (10179 : Int) * 60 > 1 * 563920 ∧
    (9451 : Int) * 700 > 26 * 213325 ∧
    (9999 : Int) * (177 * 177 * 10000) < 10000 * (177 * 177 * 10000 - 97 * 97) ∧
    (177 : Int) * 177 * 10000 < 18559 * 18559 := by
  decide

end Foundation0.ACQ
