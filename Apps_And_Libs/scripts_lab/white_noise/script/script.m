
tamanho=100;
white_noise = randn(tamanho,tamanho);

% Calcula as fun��es de correla��o, horizontal e vertical
[corr1] = construct_correlation_function_correct(2,10,white_noise);
[corr2] = construct_correlation_function_correct(10,2,white_noise);

% Gera uma simula��o teste com FFTMA, descomente a linha 12 para alternar
% entre as fun��es de correla��o vertical e horizontal:
[ simulation ] = FFT_MA_3D( corr1, white_noise );
%[ simulation ] = FFT_MA_3D( corr2, white_noise );
figure
imagesc(simulation)
title('Simula��o FFMA')

gaborArray = gaborFilterBank(5,10,10,10);
featureVector = gaborFeatures(simulation,gaborArray,4,4);
%featureVector = gaborFeatures(simulation,gaborArray,4,4);

    
%Define o filtro da rede como o filtro do FFTMA:
filtro_rede1 = fftshift(ifftn(sqrt(abs(fftn(corr1)))));
filtro_rede2 = fftshift(ifftn(sqrt(abs(fftn(corr2)))));
%Define o filtro da rede como a pr�pria fun��o de correla��o:
filtro_rede1  = corr1;
filtro_rede2  = corr2;

% Divide pela soma para ser um filtro de m�dia:
filtro_rede1  = filtro_rede1/sum(filtro_rede1(:));
filtro_rede2  = filtro_rede2/sum(filtro_rede2(:));

%Aplica as filtragens:
filtragem1 = convn(simulation,filtro_rede1,'same');
filtragem2 = convn(simulation,filtro_rede2,'same');

%Visualiza��o:
figure
imagesc(simulation)
title('Simula��o de teste')

scale = max([ max(filtragem1(:)) max(filtragem2(:)) ]);
figure
subplot(2,2,1)
imagesc(filtro_rede1)
title('Filtro Rede 1')
subplot(2,2,2)
imagesc(filtro_rede2)
title('Filtro Rede 2')
subplot(2,2,3)
imagesc(abs(filtragem1))
title('Filtragem 1')
caxis([0 scale])
subplot(2,2,4)
imagesc(abs(filtragem2))
title('Filtragem 2')
caxis([0 scale])