
(load "sort.scm")

(define len 5000)
(define data (make-vector len))
(define f-port (open-input-file "data"))
(define (get-input-data i)
  (let ((a (read f-port)))
    (if (< i len)
        (begin
          (vector-set! data i a)
          (get-input-data (+ i 1))))))

(get-input-data 0)

;(merge-sort data < 99999999)
;(merge-sort! data <)
;(insert-sort data <)
(heap-sort data < -2)

'done
