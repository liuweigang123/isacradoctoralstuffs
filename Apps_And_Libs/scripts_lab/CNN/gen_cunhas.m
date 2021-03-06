    % Este arquivo carrega os dados a serem usados como referencia na otimizacao
function [ images_hr, images_lr, gray_hr, gray_lr,randI] = gen_cunhas( num_cunhas )

    im_size = 32;
    im_dim = im_size^2;
    deslocamento_max = 32;
    profundidade_max = 32;
    cube_high =[];
    cube_low = [];
    gray_hr = [];
    gray_lr = [];
    randI=[];
    idx = 1;

    in_val = rand(1,1);
    out_val = rand(1,1);
    
    %Valores de referencia para treinamento
    max_val = 3500;
    min_val = 2500;
    
    for image=1:num_cunhas

    %espessura_cunha_max = 5 + rand*30;
    %base_cunha = 20 + rand*30;
    %tamanho_cunha = 0.40 + rand*0.30;
    
    espessura_cunha_max = 5 + rand*10;
    base_cunha = 15 + rand*10;
    tamanho_cunha = 0.40 + rand*0.30;
    
    modulo = randi(100,1);
    
    % Calcula a espessura da cunha ao longo do deslocamento
    for coluna = 1:deslocamento_max
        espessura = espessura_cunha_max - ( (espessura_cunha_max / (tamanho_cunha * deslocamento_max)) * (coluna - 1) );
        if espessura < 0
            espessura_cunha(coluna) = 0;
        else
            espessura_cunha(coluna) = espessura;
        end;
    end;



    for coluna = 1:deslocamento_max
          
        % Calcula tempo ate atingir determinada profundidade, baseado na velocidade do meio
        topo_cunha = base_cunha - espessura_cunha(coluna);
        if topo_cunha ~= base_cunha
            tempo_ate_topo_cunha(coluna) = 2 * (1000 * topo_cunha / max_val); % 1000 de milissegundos
            tempo_na_cunha(coluna) = tempo_ate_topo_cunha(coluna) + 2 * (1000 * (base_cunha - topo_cunha) / min_val);
            tempo_depois_cunha(coluna) = tempo_na_cunha(coluna) + 2 * (1000 * (profundidade_max - base_cunha) / max_val);
        else
            tempo_ate_topo_cunha(coluna) = 0;
            tempo_na_cunha(coluna) = 0;
            tempo_depois_cunha(coluna) = 2 * (1000 * profundidade_max / max_val);
        end;
        % Calcula valores de impedância em uma matriz Deslocamento x Tempo
        tempo_max = tempo_depois_cunha(1);
        for tempo = 1:tempo_max
            if tempo <= tempo_ate_topo_cunha(coluna)
                impedancia_tempo_deslocamento(tempo,coluna) = 2.6 * max_val;
            elseif tempo <= tempo_na_cunha(coluna)
                impedancia_tempo_deslocamento(tempo,coluna) = 2.4 * min_val;
            else
                impedancia_tempo_deslocamento(tempo,coluna) = 2.6 * max_val;
            end;
        end;
        for linha = 1:profundidade_max
       
        % Armazema matriz de impedância Deslocamento x Profundidade
            if image/num_cunhas < 0.33   %modulo < 33
                if linha >= topo_cunha && linha < base_cunha
                    %
                    impedancia_profundidade_deslocamento(linha,coluna) = 2.4 * min_val;
                else

                    impedancia_profundidade_deslocamento(linha,coluna) = 2.6 * max_val;
                end;
            
            else if  image/num_cunhas >=0.33 &&  image/num_cunhas < 0.66 %modulo >=33 && modulo < 66
                if linha >= topo_cunha && linha < base_cunha
                    impedancia_profundidade_deslocamento(linha,coluna) = 2.6 * max_val;
                    
                else

                    impedancia_profundidade_deslocamento(linha,coluna) = 2.4 * min_val;
                end;
                else if image/num_cunhas>0.66 %modulo>=66
                        if linha >= topo_cunha && linha < base_cunha
                            %impedancia_profundidade_deslocamento(linha,coluna) = 0.3;
                             impedancia_profundidade_deslocamento(linha,coluna) = 6500;
                        else
                            
                            %impedancia_profundidade_deslocamento(linha,coluna) = 0.7;
                             impedancia_profundidade_deslocamento(linha,coluna) = 8500;
                        end;
                    end
                end
            end
        end;
    end;

        for i = 1 : 4
            %r = randi(20,1);
            r = 8;
            ncoef = 20;
            if (length(find(impedancia_profundidade_deslocamento==0.7)) + length(find(impedancia_profundidade_deslocamento==0.3))) == im_dim 
                cube_high(:,:,idx) = imrotate(impedancia_profundidade_deslocamento, i*90);
                im_gray = cube_high(:,:,idx);
                images_hr(idx,:,:) = im_gray;
                
                gray_hr(idx,:) = reshape(cube_high(:,:,idx),1,im_size^2);
                
                %cube_low(:,:,1,idx) = lowPassFilter2(cube_high(:,:,idx),4,ncoef,r);
                cube_low(:,:,1,idx) = imrotate(lowPassFilter2(impedancia_profundidade_deslocamento,4,ncoef,r),i*90);
                %cube_low(:,:,1,idx) = imrotate(lowPassFilter2(impedancia_profundidade_deslocamento,r,150,20), i*90);
                
                im_low = imrotate(lowPassFilter2(impedancia_profundidade_deslocamento,4,ncoef,r),i*90);
                images_lr(idx,:,:) = im_low;
                
                gray_lr(:,:,1,idx) = cube_low(:,:,1,idx);
                idx = idx + 1;
            else
                cube_high(:,:,idx) = imrotate(impedancia_profundidade_deslocamento, i*90);
                gray_hr(idx,:) = reshape(mat2gray(cube_high(:,:,idx)),1,im_dim);
                %im_gray = mat2gray(cube_high(:,:,idx));
                im_gray = cube_high(:,:,idx);
                images_hr(idx,:,:) = im_gray;
                
                
                %cube_low(:,:,1,idx) = lowPassFilter2(cube_high(:,:,idx),4,ncoef,r);
                cube_low(:,:,1,idx) = imrotate(lowPassFilter2(impedancia_profundidade_deslocamento,4,ncoef,r),i*90);
                %cube_low(:,:,1,idx) = imrotate(lowPassFilter2(impedancia_profundidade_deslocamento,r,150,20), i*90);
                gray_lr(:,:,1,idx) = mat2gray(cube_low(:,:,1,idx));
                %im_low = mat2gray(imrotate(lowPassFilter2(impedancia_profundidade_deslocamento,4,ncoef,r),i*90));
                im_low = imrotate(lowPassFilter2(impedancia_profundidade_deslocamento,4,ncoef,r),i*90);
                images_lr(idx,:,:) = im_low;
                
                idx = idx + 1;
            end
%              figure; imagesc(impedancia_profundidade_deslocamento);
%              figure; imagesc(im_gray);
%              figure; imagesc(im_low);
            randI = [randI, r];
        end
    end
      
end