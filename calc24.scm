(define (accumulate op init seq)
  (if (null? seq)
      init
      (op (car seq)
          (accumulate op init (cdr seq)))))

(define (flatmap proc seq)
  (accumulate append '() (map proc seq)))

(define (enumerate-interval i j)
  (if (> i j)
      '()
      (cons i (enumerate-interval (+ i 1) j))))

(define (make-element element-list history)
  (list element-list history))

(define (get-element-list element)
  (car element))

(define (get-element-history element)
  (cadr element))

(define (generate-unique-pair n)
  ;;this proc return a list of pair(i,j),i<j
  (flatmap
   (lambda (i)
     (map (lambda (j)
            (list j i))
          (enumerate-interval 1 (- i 1))))
   (enumerate-interval 1 n)))

(define (generate-not-unique-pair n)
  (flatmap
   (lambda (i)
     (flatmap (lambda (j)
            (list (list j i) (list i j)))
          (enumerate-interval 1 (- i 1))))
   (enumerate-interval 1 n)))

(define (generate-1-class-triple n)
  (flatmap
   (lambda (p)
     (list (cons + p) (cons * p)))
   (generate-unique-pair n)))

(define (generate-2-class-triple n)
  (flatmap
   (lambda (p)
     (list (cons / p) (cons - p)))
   (generate-not-unique-pair n)))

(define (generate-choice n)
  (append (generate-1-class-triple n)
          (generate-2-class-triple n)))

(define (get-op-from-tri tri)
  (car tri))

(define (get-first-index-from-tri tri)
  (cadr tri))

(define (get-second-index-from-tri tri)
  (caddr tri))

(define (list-ref i l)
  (cond ((= i 1) (car l))
        (else (list-ref (- i 1) (cdr l)))))

(define magic 3.1415926535)

(define (get-rest l i j)
  (define (iter-helper result index rest)
    (if (null? rest)
        result
        (if (or (= index i) (= index j))
            (iter-helper result (+ index 1) (cdr rest))
            (iter-helper (append result (list (car rest)))
                         (+ index 1) (cdr rest)))))
  (iter-helper '() 1 l))

(define (extend element-list n)
  (flatmap
   (lambda (ele)
     (let ((ele-list (get-element-list ele))
           (ele-history (get-element-history ele)))
       (map
        (lambda (tri)
          (let ((op (get-op-from-tri tri))
                (first-index (get-first-index-from-tri tri))
                (second-index (get-second-index-from-tri tri)))
            (let ((rest-list (get-rest ele-list first-index second-index))
                  (first-number (list-ref first-index ele-list))
                  (second-number (list-ref second-index ele-list)))
              (if (and (eq? op /) (= second-number 0))
                  (make-element (cons magic rest-list) '())
                  (make-element (cons (op first-number second-number) rest-list)
                                (append ele-history (list tri)))))))
        (generate-choice n))))
   element-list))

(define (change ele-hist)
  (map
   (lambda (item)
     (let ((op (car item))
           (rest (cdr item)))
       (cond ((eq? op +) (cons '+ rest))
             ((eq? op -) (cons '- rest))
             ((eq? op *) (cons '* rest))
             ((eq? op /) (cons '/ rest)))))
   ele-hist))

(define (print-ans result)
  (for-each
   (lambda (ele)
     (let ((ele-list (get-element-list ele))
           (ele-hist (get-element-history ele)))
       (display ele-list)
       (display ": ")
       (display (change ele-hist))
       (newline)))
   result))
