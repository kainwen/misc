;A red black tree is firstly a binary search tree.
;Then in order to be called red-black, we must color the nodes
;under some rules.

;---------------------------------------------------------------------
;first let us write the node data structure
;its state property :
;     1. key
;     2. color
;     3. satellite data
;     (above 3 is passed by the user when call 'make-node' proc
;     4. parent
;     5. right
;     6. left
;     (4-6 is the pointer to other node, '() when is nil)
;its interface proc :
;     1. about get info :
;         1.1 get-parent
;         1.2 get-right
;         1.3 get-left
;         1.4 get-key
;         1.5 get-satellite
;         1.6 get-color
(define RED 1)
(define BLACK 0)
(define (make-node k s c)
  (let ((parent '())
        (right '())
        (left '())
        (key k)
        (satellite s)
        (color c))
    (define (set-parent! p)
      (set! parent p))
    (define (set-right! r)
      (set! right r))
    (define (set-left! l)
      (set! left l))
    (define (set-key! k)
      (set! key k))
    (define (set-satellite! s)
      (set! satellite s))
    (define (set-color! c)
      (set! color c))
    (define (dispatch message)
      (cond ((eq? message 'get-parent) parent)
            ((eq? message 'get-right) right)
            ((eq? message 'get-left) left)
            ((eq? message 'get-key) key)
            ((eq? message 'get-satellite) satellite)
            ((eq? message 'get-color) color)
            ((eq? message 'set-parent) set-parent!)
            ((eq? message 'set-right) set-right!)
            ((eq? message 'set-left) set-left!)
            ((eq? message 'set-key) set-key!)
            ((eq? message 'set-satellite) set-satellite!)
            ((eq? message 'set-color) set-color!)
            (else (error "Unknown request -- NODE" message))))
    dispatch))

(define (get-key node)
  (if (null? node)
      '()
      (node 'get-key)))
(define (get-parent node)
  (if (null? node)
      '()
      (node 'get-parent)))
(define (get-right node)
  (if (null? node)
      '()
      (node 'get-right)))
(define (get-left node)
  (if (null? node)
      '()
      (node 'get-left)))
(define (get-color node)
  (if (null? node)
      BLACK
      (node 'get-color)))
(define (get-satellite node) (node 'get-satellite))

(define (set-key! node k) ((node 'set-key) k))
(define (set-parent! node p) ((node 'set-parent) p))
(define (set-right! node r) ((node 'set-right) r))
(define (set-left! node l) ((node 'set-left) l))
(define (set-color! node c) ((node 'set-color) c))
(define (set-satellite! node s) ((node 'set-satellite) s))
; we never do operation "get or set" for a NIL!!!!!!!!!!!!
(define (connect-nodes-lc l p)
  (begin (set-left! p l)
         (if (not (null? l))
             (set-parent! l p))))

(define (connect-nodes-rc r p)
  (begin (set-right! p r)
         (if (not (null? r))
             (set-parent! r p))))

(define (cmp-node f n1 n2) (f (get-key n1) (get-key n2)))

;---------------------------------------------------------------------
;let us write the red black tree
;---------------------------------------------------------------------
;first, recall what we mean by "Red Black Tree"
;A Binary Tree can be called a Red Black Tree if and if only it holds
;the following 5 prooperties  :
;1. Each node is either red or black
;2. The root is black
;3. Each leaf(NIL) is black
;4. if a node is red , then both its children are black.
;5. For each node, all paths from the node to descendant leaves contain
;   the same number of black nodes.
;----------------------------------------------------------------------
;its state property :
;     1. root
(define (make-rbt f)
  (let ((root '())
        (cmp (lambda (n1 n2) (f (get-key n1) (get-key n2)))))
    (define (in-order-walk r)
      (if (null? r)
          '()
          (append (in-order-walk (get-left r))
                    (list (cons (get-key r) (get-color r)))
                    (in-order-walk (get-right r)))))

    (define (level-walk queue)
      (if (or (null? queue))
          '()
          (let ((to-visit (car queue)))
            (begin (set! queue (cdr queue))
                   (if (not (null? (get-left to-visit)))
                       (set! queue (append queue (list (get-left to-visit)))))
                   (if (not (null? (get-right to-visit)))
                       (set! queue (append queue (list (get-right to-visit)))))
                   (append (list (cons (get-key to-visit)
                                       (get-color to-visit)))
                           (level-walk queue))))))


    (define (search r k)
      (cond ((or (null? r)
                 (eq? k (get-key r))) r)
            ((f k (get-key r)) (search (get-left r) k))
            (else (search (get-right r) k))))
    (define (minimum r)
      (cond ((null? r) (error "Empty Tree!"))
            (else
             (let ((l (get-left r)))
               (if (null? l)
                   r
                   (minimum l))))))

    (define (maximum r)
      (cond ((null? r) (error "Empty Tree!"))
            (else
             (let ((ri (get-right r)))
               (if (null? ri)
                   r
                   (maximum ri))))))
    (define (successor-iter-help x y)
      (cond ((or (null? y) (not (eq? x (get-right y)))) y)
            (else (successor-iter-help y (get-parent y)))))
    (define (successor x)
      (cond ((null? x) (error "Empty Tree!"))
            (else
             (let ((r (get-right x)))
               (if (null? r)
                   (successor-iter-help x (get-parent x))
                   (minimum r))))))
    (define (predecessor-iter-help x y)
      (cond ((or (null? y) (not (eq? x (get-left y)))) y)
            (else (predecessor-iter-help y (get-parent y)))))
    (define (predecessor x)
      (cond ((null? x) (error "Empty Tree!"))
            (else
             (let ((l (get-left x)))
               (if (null? l)
                   (predecessor-iter-help x (get-parent x))
                   (maximum l))))))

;   |       Left-Rotate(x)            |
;   x      ---------------->          y
;  / \                               / \
; a   y    <----------------        x   c
;    / \    Right-Rotate(y)        / \
;   b   c                         a   b
    (define (left-rotate x)
      (let ((y (get-right x)))
        (if (null? y)
            (error "Right Child is NIL!!!" x)
            (begin (connect-nodes-rc (get-left y) x)
                   (if (null? (get-parent x))
                       (begin (set-parent! y '())
                              (set! root y))
                       (if (eq? x (get-left (get-parent x)))
                           (connect-nodes-lc y (get-parent x))
                           (connect-nodes-rc y (get-parent x))))
                   (connect-nodes-lc x y)))))
    (define (right-rotate y)
      (let ((x (get-left y)))
        (if (null? x)
            (error "Left Child is NIL!!!" y)
            (begin (connect-nodes-lc (get-right x) y)
                   (if (null? (get-parent y))
                       (begin (set-parent! x '())
                              (set! root x))
                       (if (eq? y (get-right (get-parent y)))
                           (connect-nodes-rc x (get-parent y))
                           (connect-nodes-lc x (get-parent y))))
                   (connect-nodes-rc y x)))))
    ;rember the loop invariant:
    ;1. Node z is red ;
    ;2. if (get-parent z) is root, the (get-parent z) is black
    ;3. if there is a violation of the rbt, there's at most one!
    ;   either Property 2 : z is root, and z is red
    ;       or Property 4 : both z and (get-parent z) are red.
    ;----------------------------case  1----------------------------
    ;                |                                      |
    ;            (BLACK:C)                                (RED:C)
    ;             /       \                              /       \
    ;         (RED:A)     (RED:D) --------->       (BLACK:A)     (BLACK:D)
    ;         /   \           / \                  /    \           / \
    ;        a    (RED:z)    d   e                a    (RED:z)     d   e
    ;              /  \                                 /  \
    ;             b    c                               b    c
    ;-------------------------another case 1-------------------------
    ;                |                                      |
    ;            (BLACK:C)                                (RED:C)
    ;             /       \                              /       \
    ;         (RED:A)     (RED:D) --------->       (BLACK:A)     (BLACK:D)
    ;         /   \           / \                  /    \           / \
    ;     (RED:z)  c         d   e             (RED:z)   c         d   e
    ;      /  \                                 /  \
    ;     a    b                               a    b
    ;-------------case 2------------case 3-------------------------------
    ;              |                    |                   |
    ;          (BLACK:C) ------>    (BLACK:C)  ------>   (BLACK:z)
    ;           /   \                /    \               /    \
    ;       (RED:A)  d          (RED:z)    d         (RED:A)    (RED:C)
    ;       /  \                  /    \              /  \        /  \
    ;      a   (RED:z)         (RED:A)  c            a    b      c    d
    ;           /  \            /  \
    ;          b    c          a    b
    (define (get-uncle z right-uncle?)
      (if right-uncle?
          (get-right (get-parent (get-parent z)))
          (get-left (get-parent (get-parent z)))))
    (define (need-first-rotate? z p right-uncle?)
      (if right-uncle?
          (eq? z (get-right p))
          (eq? z (get-left p))))
    (define (select-rotate flag)
      (if flag
          left-rotate
          right-rotate))
    (define (get-rotate-proc message flag)
      ;(if (eq? message 'first)
          ;(if right-uncle? left-rotate right-rotate)
          ;(if right-uncle? right-rotate left-rotate))
      (cond ((eq? message 'first) (select-rotate flag))
            ((eq? message 'second) (select-rotate (not flag)))
            ((eq? message 'third) (select-rotate (not flag)))
            ((eq? message 'fourth) (select-rotate flag))
            (else (error "Unknown message" messaga))))
    (define (insert-fixup z)
      (let ((p (get-parent z)))
        (if (eq? (get-color p) RED)
            (let ((gp (get-parent (get-parent z))))
              (let ((right-uncle? (eq? p (get-left gp))))
                (let ((y (get-uncle z right-uncle?)))
                  (if (eq? (get-color y) RED)
                      (begin (set-color! p BLACK)
                             (set-color! y BLACK)
                             (set-color! gp RED)
                             (insert-fixup gp))
                      (begin (if (need-first-rotate? z p right-uncle?)
                                 (begin (set! z p)
                                        ((get-rotate-proc 'first right-uncle?) z)))
                             (let ((np (get-parent z)))
                               (let ((ngp (get-parent np)))
                                 (begin (set-color! np BLACK)
                                        (set-color! ngp RED)
                                        ((get-rotate-proc 'second right-uncle?) ngp)
                                        (insert-fixup ngp)))))))))
            (set-color! root BLACK))))
    (define (insert-iter-help x y z)
      (cond ((null? x)
             (begin
               (if (cmp z y)
                   (connect-nodes-lc z y)
                   (connect-nodes-rc z y))
               (set-color! z RED)
               (insert-fixup z)))
            ((cmp z x) (insert-iter-help (get-left x) x z))
            (else (insert-iter-help (get-right x) x z))))
    (define (insert z)
      (cond ((null? root)
             (begin (set! root z)
                    (set-color! z BLACK)))
            (else
             (insert-iter-help root '() z))))

    (define (choose-y z)
      (if (or (null? (get-left z))
              (null? (get-right z)))
          z
          (successor z)))
    (define (choose-x y)
      (if (null? (get-left y))
          (get-right y)
          (get-left y)))
    (define (get-child message x flag)
      ;(cond ((or (eq? message 'start) (eq? message 'first) (eq? message 'second) (eq? message 'fourth))
      (cond ((eq? message 'ok)
             (if flag (get-right x) (get-left x)))
            ((eq? message 'third)
             (if flag
                 (lambda (before?) (if before? (get-left x) (get-right x)))
                 (lambda (before?) (if before? (get-right x) (get-left x)))))))
    (define (delete-fixup x)
      (if (or (eq? x root) (eq? (get-color x) RED))
          (set-color! x BLACK)
          (let ((p (get-parent x)))
            (let ((right-brother? (eq? x (get-left p))))
              (let ((w (get-child 'ok p right-brother?)))
                (begin
                  (if (eq? (get-color w) RED)
                      (begin (set-color! w BLACK) ;this is case1
                             (set-color! p RED)
                             ((get-rotate-proc 'first right-brother?) p)
                             (set! w (get-child 'ok p right-brother?))))
                  (if (and (eq? (get-color (get-left w)) BLACK)
                           (eq? (get-color (get-right w)) BLACK))
                      (begin (set-color! w RED); this is case2
                             (delete-fixup p))
                      (begin
                        (if (eq? (get-color (get-child 'ok w right-brother?)) BLACK)
                            (begin (set-color! ((get-child 'third w right-brother?) #t) BLACK)
                                   (set-color! w RED)
                                   ((get-rotate-proc 'third right-brother?) w)
                                   (set! w ((get-child 'third p right-brother?) #f))))
                        (set-color! w (get-color p))
                        (set-color! p BLACK)
                        (set-color! (get-child 'ok w right-brother?) BLACK)
                        ((get-rotate-proc 'fourth right-brother?) p)
                        (set! x root)
                        (delete-fixup x)))))))))
    (define (delete z)
      (cond ((eq? root z) (set! root '()))
            (else
             (let ((y (choose-y z)))
               (let ((x (choose-x y))
                     (p (get-parent y)))
                 (begin (if (null? p)
                            (set! root x)
                            (if (eq? y (get-left p))
                                (connect-nodes-lc x p)
                                (connect-nodes-rc x p)))
                        (if (not (eq? y z))
                            (begin (set-key! z (get-key y))
                                   (set-satellite! z (get-satellite y))))
                        (if (eq? (get-color y) BLACK)
                            (delete-fixup x))))))))

    (define (dispatch message)
      (cond ((eq? message 'insert) insert)
            ((eq? message 'in-order-walk) (in-order-walk root))
            ((eq? message 'level-walk) (level-walk (list root)))
            ((eq? message 'search) (lambda (k) (search root k)))
            ((eq? message 'minimum) minimum)
            ((eq? message 'maximum) maximum)
            ((eq? message 'successor) successor)
            ((eq? message 'predecessor) predecessor)
            ((eq? message 'left-rotate) left-rotate)
            ((eq? message 'right-rotate) right-rotate)
            ((eq? message 'insert) insert)
            ((eq? message 'delete) delete)
            (else (error "Unknown Message!" message))))
    dispatch))

(define (insert rbt n) ((rbt 'insert) n))
(define (delete rbt z) ((rbt 'delete) z))
(define (in-order-walk rbt) (rbt 'in-order-walk))
(define (level-walk rbt) (rbt 'level-walk))
(define (search rbt k) ((rbt 'search) k))

