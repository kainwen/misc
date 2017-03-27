(define shared-variable 100)

(define tmp-variable 0)

(define seq '((p2) (p1a p1b)))

(define (accumulate op init l)
  (if (null? l)
      init
      (op (car l)
          (accumulate op init (cdr l)))))

(define (flatmap proc seq)
  (accumulate append '() (map proc seq)))

(define (myproc x seq)
  (if (eq? x (caar seq))
      (cons (cdr (car seq)) (cdr seq))
      (cons (car seq) (myproc x (cdr seq)))))

(define (make-all-path seq)
  (cond ((null? seq) '(()))
        (else
         (let ((first (map car seq)))
           (flatmap
            (lambda (x)
              (map (lambda (l)
                     (cons x l))
                   (make-all-path
                    (filter (lambda (s) (not (null? s)))
                            (myproc x seq)))))
            first)))))

(define all_seq (make-all-path seq))

