//http://poj.org/problem?id=3601

#include <stdio.h>

int a[102] ;
int b[102] ;
int c[102] ;

int main(){
    int n , m ;
    while ( scanf("%d%d",&n,&m)!=EOF ){
	//n block
	//mod m
	int i ;
	for ( i = 1 ; i <= n ; i++ ) {
	    scanf("%d",&a[i]);
	}
	b[1] = (2*a[1] - 1) % m;
	c[1] = a[1] % m ;
	for ( i = 2 ; i <= n ;i++ ) {
	    if( a[i] > 1 ) 
		b[i] = (b[i-1] + ((2*c[i-1])%m) + ((2*a[i])%m))%m ;
	    else 
		b[i] = (2*c[i-1] + 1)%m ;
	    c[i] = (2*c[i-1] + (a[i]%m))%m ;
	}
	printf("%d\n",b[n]) ;
    }
    return  0 ;
}
