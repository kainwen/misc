/* 
 * Tecent Intern Coding Problem for 2013 summer,
 * I manage to work it out in the exam.
 *
 * Byr Link: https://bbs.byr.cn/#!article/ACM_ICPC/70518
 *
 * 已知数组a[n],构造数组b[n] 使b[i]=a[0]*a[1]...a[n-2]*a[n-1]/a[i]
 * 要求不能用除法
 * 除遍历计数器与a[N] b[N]外，不可使用新的变量(包括栈临时变量、对空间和全局静态变量等)
 * 空间复杂度o(1)  时间复杂度o(n)
 */

#include <stdio.h>
#define N 5
int main() {
    int i ;
    int a[N]={1,2,3,4,5} ;
    int b[N] ;
    b[0] = 1 ;
    for(i=0;i<N-1;i++){
        b[0] *= a[i] ;
        b[i+1] = b[0] ;
    }
    b[0] = 1 ;
    for(i=N-1;i>=2;i--){
        b[0] *= a[i] ;
        b[i-1] *= b[0] ;
    }
    b[0] *= a[1] ;
    for(i=0;i<N;i++) printf("%d ",b[i]) ;
    return 0 ;
}
