Inductive t : Type :=
| zhen (* represent true *)
| jia  (* represent false *)
| if_stat : t -> t -> t -> t.

Inductive eval_small_step : t -> t -> Prop :=
| ev_if_true : forall (t2 t3 : t),
    eval_small_step (if_stat zhen t2 t3) t2
| ev_if_false : forall (t2 t3 : t),
    eval_small_step (if_stat jia t2 t3) t3
| ev_if : forall (t1 t2 t3 t4 : t),
    eval_small_step t1 t2 ->
    eval_small_step (if_stat t1 t3 t4) (if_stat t2 t3 t4).

Theorem determinacy : forall (t1 t2 t3 : t),
    eval_small_step t1 t2 -> eval_small_step t1 t3 -> t2 = t3.

Proof.
  intros t1 t2 t3.
  intros H1.
  revert t3.
  induction H1.
  - intros t0. intros H.
    inversion H.
    + reflexivity.
    + inversion H4.
  - intros t0. intros H.
    inversion H.
    + reflexivity.
    + inversion H4.
  - intros t0.
    intros H.
    assert(H': eval_small_step (if_stat t1 t3 t4) (if_stat t2 t3 t4)).
    {
      apply ev_if. apply H1.
    }
    inversion H.
    + rewrite <- H2 in H1. inversion H1.
    + rewrite <- H2 in H1. inversion H1.
    + assert(H'': t2 = t6).
      {
        apply IHeval_small_step.
        apply H5.
      }
      rewrite H''. reflexivity.
Qed.
