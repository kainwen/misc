#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>
#include <limits.h>

int stack[128] = {0};
int stack_pointer = -1;

/*
 * ===================================================================
 * Basic Type System (copied from Postgres)
 * ===================================================================
 */
typedef enum NodeTag
{
  T_Item = 0,
  T_Option
} NodeTag;

typedef struct Node {
  NodeTag   type;
} Node;

#define nodeTag(nodeptr) (((const Node*)(nodeptr))->type)
#define newNode(size, tag) \
({	Node   *_result; \
	assert((size) >= sizeof(Node));		/* need the tag, at least */ \
	_result = (Node *) calloc(1, size);   \
	_result->type = (tag); \
	_result; \
})
#define makeNode(_type_)       ((_type_ *) newNode(sizeof(_type_),T_##_type_))
#define NodeSetTag(nodeptr,t)  (((Node*)(nodeptr))->type = (t))
#define IsA(nodeptr,_type_)    (nodeTag(nodeptr) == T_##_type_)

typedef struct LinkNode LinkNode;
struct LinkNode {
  NodeTag   type;
  LinkNode *prev;
  LinkNode *next;
};

typedef struct Item {
  LinkNode ln;
  int      name;
} Item;

typedef struct Option {
  LinkNode ln;
  union {
    int len;
    int top;
  } info;
  int pos;
  int i;
  int j;
} Option;

#define ULINK(x) (((LinkNode *) x)->prev)
#define DLINK(x) (((LinkNode *) x)->next)
#define LLINK(x) (((LinkNode *) x)->prev)
#define RLINK(x) (((LinkNode *) x)->next)

typedef struct Model {
  LinkNode  **node_pool;
  int         n_total_nodes;
  int         n_option_heads;
  Item       *item_head;
  Item      **item_pool;
} Model;

/*
 * ===================================================================
 * Function Declartions for Doubly LinkList APIs
 * ===================================================================
 */
void set_head(LinkNode *head);
void remove_node(LinkNode *x);
void undo_remove(LinkNode *x);
void insert(LinkNode *head, LinkNode *x);
bool is_empty_list(LinkNode *x);
void print(LinkNode *x);
/*
 * ===================================================================
 * Function Declartions for Exact Covering Problem
 * ===================================================================
 */
int count_matrix_ones(int **matrix, int nrows, int ncols);
void create_items(Model *model, int n);
Model *create_model(int **matrix, int nrows, int ncols);
void cover(Model *model, Item *item);
void hide(Model *model, Option *p);
void uncover(Model *model, Item *item);
void unhide(Model *model, Option *p);
Item *pick_mrv_item(Model *model, Item *item_head);
void algorithmX(Model *model);
void print_model(Model *model);

/*
 * ===================================================================
 * Function Implementations for Doubly LinkList APIs
 * ===================================================================
 */
void
set_head(LinkNode *head)
{
  LLINK(head) = RLINK(head) = head;
}

void
remove_node(LinkNode *x)
{
  LinkNode *l = LLINK(x);
  LinkNode *r = RLINK(x);
  LLINK(r) = l;
  RLINK(l) = r;
}

void
undo_remove(LinkNode *x)
{
  LinkNode *l = LLINK(x);
  LinkNode *r = RLINK(x);
  LLINK(r) = x;
  RLINK(l) = x;
}

void
insert(LinkNode *head, LinkNode *x)
{
  LinkNode *tail = LLINK(head);

  RLINK(tail) = x;
  LLINK(x) = tail;
  LLINK(head) = x;
  RLINK(x) = head;

  if (IsA(head, Option)) {
    ((Option *) head)->info.len++;
  }
}

bool
is_empty_list(LinkNode *x)
{
  return LLINK(x) == RLINK(x) && LLINK(x) == x;
}

void
print(LinkNode *x)
{
  LinkNode *n = RLINK(x);
  while (x != n) {
    if (IsA(n, Item)) {
      printf("%d ", ((Item *) n)->name);
    }
    else if (IsA(n, Option)) {
      printf("%d ", ((Option *) n)->pos);
    }
    n = RLINK(n);
  }
  printf("\n");
}

/*
 * ===================================================================
 * Function Implementations for Exact Covering Problem
 * ===================================================================
 */

int
count_matrix_ones(int **matrix, int nrows, int ncols)
{
  int n = 0;
  for (int i = 0; i < nrows; i++)
    for (int j = 0; j < ncols; j++)
      if (matrix[i][j] == 1) n++;

  return n;
}

void
print_model(Model *model)
{
  printf("Items: ");
  print((LinkNode *) model->item_head);
  Item *item = (Item *) RLINK((LinkNode *) model->item_head);
  while (item != model->item_head) {
    printf("Col %d: ", item->name);
    print(model->node_pool[item->name]);
    item = (Item *) RLINK((LinkNode *) item);
  }
  printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
}

void
create_items(Model *model, int n)
{
  Item  *head = (Item *) makeNode(Item);
  Item **item_pool = (Item **) calloc(n+1, sizeof(Item*));
  head->name = 0;
  set_head((LinkNode *) head);
  for (int i = 1; i <= n; i++) {
    Item *x = (Item *) makeNode(Item);
    x->name = i;
    insert((LinkNode *) head, (LinkNode *) x);
    item_pool[i] = x;
  }
  model->item_head = head;
  model->item_pool = item_pool;
}

Model *
create_model(int **matrix, int nrows, int ncols)
{
  Model *model;
  model = (Model *) calloc(1, sizeof(Model));

  /* init items */
  create_items(model, ncols);

  int n_ones = count_matrix_ones(matrix, nrows, ncols);
  int n_spacers = nrows + 1;
  int n_total_nodes = ncols + n_ones + n_spacers + 1; /* waste the idx=0 node */

  /* 
   * init the node pool
   *   idx: 0 (waste, no use)
   *   idx: [1, ncols] (option heads)
   *   left: option nodes
   */
  model->node_pool = (LinkNode  **) calloc(n_total_nodes, sizeof(LinkNode  *));
  model->n_total_nodes = n_total_nodes;
  model->n_option_heads = ncols;

  /* init option heads */
  for (int i = 1; i <= ncols; i++) {
    Option *ohead = (Option *) makeNode(Option);
    ohead->pos = i;
    set_head((LinkNode *) ohead);
    ohead->info.len = 0;
    model->node_pool[i] = (LinkNode *) ohead;
  }

  /* create all options */
  int pos = ncols + 1;

  /* create the first spacer */
  Option *first_spacer = (Option *) makeNode(Option);
  first_spacer->info.top = 0;
  first_spacer->pos = pos;
  int last_spacer_pos = pos;
  model->node_pool[pos++] = (LinkNode *) first_spacer;
  
  for (int i = 0; i < nrows; i++) {
    /* one row is an option */
    bool first = true;
    int first_pos = -1;
    for (int j = 0; j < ncols; j++) {
      /* whole row is 0 make no sense, we do not consider it */
      if (matrix[i][j] == 1) {
	if (first) {
	  first = false;
	  first_pos = pos;
	}
	Option *op = (Option *) makeNode(Option);
	op->i = i;
	op->j = j;
	op->pos = pos;
	op->info.top = j+1;
	model->node_pool[pos++] = (LinkNode *) op;
	insert((LinkNode *) model->node_pool[j+1], (LinkNode *) op);
      }
    }
    /* now pos-1 contains the last option node's pos */
    Option *last_spacer = (Option *) model->node_pool[last_spacer_pos];
    DLINK(last_spacer) = model->node_pool[pos-1];
    /* insert a new spacer */
    Option *sp = (Option *) makeNode(Option);
    sp->info.top = last_spacer->info.top - 1;
    sp->pos = pos;
    ULINK(sp) = model->node_pool[first_pos];
    last_spacer_pos = pos;
    model->node_pool[pos++] = (LinkNode *) sp;
  }

  assert(pos == n_total_nodes);
  return model;
}

void
cover(Model *model, Item *item)
{
  int name = item->name;
  LinkNode *vhead = model->node_pool[name];
  LinkNode *p = DLINK(vhead);
  while (p != vhead) {
    assert(IsA(p, Option));
    hide(model, (Option *) p);
    p = DLINK(p);
  }
  remove_node((LinkNode *) item);
}

void
hide(Model *model, Option *p)
{
  int q = p->pos + 1;
  LinkNode *lq = model->node_pool[q];
  while (((void *) p) != ((void *) lq)) {
    int top = ((Option *) lq)->info.top;
    if (top <= 0) {
      lq = ULINK(lq); /* loop back */
      q = ((Option *) lq)->pos;
    }
    else {
      remove_node(lq);
      LinkNode *hd = model->node_pool[((Option *) lq)->info.top];
      ((Option *) hd)->info.len--;
      q++;
      lq = model->node_pool[q];
    }
  }
}

void
uncover(Model *model, Item *item)
{
  int name = item->name;
  undo_remove((LinkNode *) item);
  LinkNode *vhead = model->node_pool[name];
  LinkNode *p = ULINK(vhead);

  while (p != vhead) {
    assert(IsA(p, Option));
    unhide(model, (Option *) p);
    p = ULINK(p);
  }
}

void
unhide(Model *model, Option *p)
{
  int q = p->pos - 1;
  LinkNode *lq = model->node_pool[q];
  while (((void *) p) != ((void *) lq)) {
    int top = ((Option *) lq)->info.top;
    if (top <= 0) {
      lq = DLINK(lq);
      q = ((Option *) lq)->pos;
    }
    else {
      undo_remove(lq);
      LinkNode *hd = model->node_pool[((Option *) lq)->info.top];
      ((Option *) hd)->info.len++;
      q--;
      lq = model->node_pool[q];
    }
  }
}

Item *
pick_mrv_item(Model *model, Item *item_head)
{
  int   min_len = INT_MAX;
  Item *item = (Item *) RLINK((LinkNode *) item_head);
  Item *item_to_pick = NULL;
  while (item != item_head) {
    int name = item->name;
    Option *head = (Option *) model->node_pool[name];
    if (head->info.len < min_len) {
      min_len = head->info.len;
      item_to_pick = item;
    }
    item = (Item *) RLINK((LinkNode *) item);
  }
  return item_to_pick;
}

void
algorithmX(Model *model)
{
  /* 1. pick an item to cover (using MRV) */
  Item   *item = pick_mrv_item(model, model->item_head);

  if (item == NULL) {
    for (int i = 0; i <= stack_pointer; i++) {
      int pos = stack[i];
      printf("%d ",  ((Option *) (model->node_pool[pos]))->i);
    }
    printf("\n");
    return;
  }

  Option *ohead = (Option *) model->node_pool[item->name];
  /* 2. Cover the Item */
  cover(model, item);
  /* 3. loop all options involving the item */
  Option *op = (Option *) DLINK((LinkNode *) ohead);
  while (op != ohead) {
    stack[++stack_pointer] = op->pos;
    /* cover all items in the option op */
    int p = op->pos + 1;
    Option *lp = (Option *) model->node_pool[p];
    while (op != lp) {
      int top = lp->info.top;
      if (top <= 0) {
	lp = (Option *) ULINK(lp);
	p = lp->pos;
      } else {
	Option *head_p = (Option *) model->node_pool[top];
	Item   *item_p = model->item_pool[head_p->pos];
	cover(model, item_p);
	p++;
	lp = (Option *) model->node_pool[p];
      }
    }
    /* rec to a sub problem */
    algorithmX(model);
    /* now try to recover the last status */
    p = op->pos - 1;
    lp =  (Option *) model->node_pool[p];
    while (op != lp) {
      int top = lp->info.top;
      if (top <= 0) {
	lp = (Option *) DLINK(lp);
	p = lp->pos;
      } else {
	Option *head_p = (Option *) model->node_pool[top];
	Item   *item_p = model->item_pool[head_p->pos];
	uncover(model, item_p);
	p--;
	lp = (Option *) model->node_pool[p];
      }
    }
    --stack_pointer;
    op = (Option *) DLINK((LinkNode *) op);
  }

  uncover(model, item);
}

int main()
{
  for(int i = 0; i < 128; i++)
    stack[i] = -1;
  
  Model *model;
  int **matrix;
  int nrows, ncols;
  scanf("%d %d", &nrows, &ncols);
  matrix = (int **) malloc(sizeof(int *) * nrows);
  for (int i = 0; i < nrows; i++) {
    matrix[i] = (int *) malloc(sizeof(int) * ncols);
    for (int j = 0; j < ncols; j++) {
      scanf("%d", &(matrix[i][j]));
    }
  }
  model = create_model(matrix, nrows, ncols);
  algorithmX(model);
  
  return 0;
}
