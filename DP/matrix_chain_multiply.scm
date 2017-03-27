(define MAXINT 99999999)

(define (matrix_best_multiply vec start_index end_index)
  (if (= start_index end_index)
      0
      (find_best_iter vec start_index end_index start_index (list MAXINT))))

(define (find_best_iter vec start_index end_index k PRE_BEST)
  (if (= k end_index)
      (car PRE_BEST)
      (let ((prefix (matrix_best_multiply vec start_index k))
            (backfix (matrix_best_multiply vec (+ 1 k) end_index)))
        (let ((now (+ prefix backfix (* (vector-ref vec start_index)
                                        (vector-ref vec (+ 1 k))
                                        (vector-ref vec (+ 1 end_index))))))
          (if (> now (car PRE_BEST))
              (find_best_iter vec start_index end_index (+ 1 k) PRE_BEST)
              (find_best_iter vec start_index end_index (+ 1 k) (list now k)))))))
