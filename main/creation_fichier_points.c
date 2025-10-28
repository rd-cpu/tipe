#include <stdio.h>

int f(int a,int b,int c,int x) {
	return x*x*x + a*x*x + b*x + c;
}

int main(){
	int a;
	int b;
	int c;
	int o;
	printf("Rentrez a : ");
	scanf("%d",&a);
	printf("Rentrez b : ");
	scanf("%d",&b);
	printf("Rentrez c : ");
	scanf("%d",&c);
	printf("Rentrez o : ");
	scanf("%d",&o);

	char filename[255];
	sprintf(filename,"pointsCEs/points_%d_%d_%d_%d.txt",a,b,c,o);

	FILE *file = fopen(filename, "w");
    	if (file == NULL) {
        	printf("Erreur d'ouverture du fichier.\n");
        return 1;
    	}

	for (int x=0; x < o; x++) {
		int fx_mod = f(a,b,c,x) % o;
        	if (fx_mod < 0) fx_mod += o;  // S'assurer que le modulo est positif
        	for (int y = 0; y < o; y++) {
            		int y2_mod = (y * y) % o;
            		if (y2_mod == fx_mod) {
						if (b == 0)
                			fprintf(file, "(%d, %d) from Courbe elliptique  y² = x³ + %dx² + %d mod %d\n",x,y,a,c,o);
						else
						 	fprintf(file, "(%d, %d) from Courbe elliptique  y² = x³ + %dx² + %dx + %d mod %d\n",x,y,a,b,c,o);

            }
        }

	}
	printf("l'ensemble des points a été retranscrit dans le fichier %s",filename);

	return 0;
}
