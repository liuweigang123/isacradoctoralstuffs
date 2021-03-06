      %[cunhas_hr, cunhas_lr, gray_hr, gray_lr] = gen_cunhas(1);
      
      [x_train, y_train] = Read_Real_Data_Guinter();
      
      [x_train, y_train] = zero_pad_images(x_train,y_train);
      [l,c,p] = size(x_train);
      
      imsInd = randi(p,1,4);
      
      lr_ims = x_train(:,:,imsInd);
      hr_ims = y_train(:,:,imsInd);
      
      fft_analisys(lr_ims,hr_ims);
      
      outputdim = l*c;
      [x_train, y_train] = norm_data(x_train,y_train);
      [gray_lr, gray_hr] = format_data_to_cnn(x_train,y_train);
% 
    layers = [ ...
        imageInputLayer([l c 1])
        
        convolution2dLayer( 5, 60, 'Stride', 1, 'Padding', 1)
        maxPooling2dLayer(2,'Stride',2);
        %dropoutLayer(0.2,'Name','dropout1')
        reluLayer
        convolution2dLayer( 5, 60, 'Stride', 1, 'Padding', 1)
        maxPooling2dLayer(2,'Stride',2);
        %dropoutLayer(0.2,'Name','dropout2')
       
        reluLayer
        fullyConnectedLayer(outputdim)
        regressionLayer
        
        ];

    options = trainingOptions('sgdm','InitialLearnRate',0.001, ...
        'MaxEpochs',250,'MiniBatchSize',100);

    net = trainNetwork(gray_lr,gray_hr,layers,options);
    save 'trained_net_with_dropout.mat' net
%    
% %% F
%load trained_net_1.mat
%load net_result_3_nov.mat
[cunhas_hr, cunhas_lr,im_hr,im_lr,randI] = gen_cunhas(1);
%im_pred = predict(net,im_lr);

%[im_hr,im_lr] = gen_cunhas_ang(4); randI=[4, 4, 4, 4];

im_pred = predict(net,im_lr);

% load workspace_teste.mat
% im_test = [];
k=1;

fig = figure;
for i=1:4
   k=4*i-3;
   sintetic = reshape(im_hr(i,:),32,32);
   blured = im_lr(:,:,i);
   cnn = reshape(im_pred(i,:),32,32);
   %subplot(1,2,1);imagesc(sintetic);subplot(1,2,2); imagesc(blured);set(gcf,'color','w')
   
   
   cnn_fourier = fourier_transform(cnn);
   sintetic_fourier = fourier_transform(sintetic);
   blured_fourier = fourier_transform(blured);

   [cnnmatches, cnn_inds] = fourier_indices_calculate(cnn, sintetic, cnn_fourier,sintetic_fourier);
   [bluredmatches, blured_inds] = fourier_indices_calculate(blured, sintetic, blured_fourier,sintetic_fourier);
   
   colormap(gray)
   set(gcf,'color','w')
   
   subplot(4,4,k)
   imagesc(sintetic)
   colorbar
   title('Synthetic');
   
   
   subplot(4,4,k+1)
   
   imagesc(blured)
   colorbar
   mse = MRSE(blured,sintetic);
   tit = strcat('Blurred (',mat2str(randI(i)),' Hz)');
   text = strcat('MSE.: ',mat2str(mse));
   text2 = strcat('FFTI.: ',mat2str(blured_inds));
   title({tit,text,text2});
   
   subplot(4,4,k+2)
   imagesc(cnn)
   colorbar
   mse = MRSE(cnn,sintetic);
   tit = 'CNN';
   text = strcat('MSE.: ',mat2str(mse));
   text2 = strcat('IFFT.: ',mat2str(cnn_inds));
   title({tit,text,text2});
   
   calcfrequencies(sintetic,blured,cnn,k+3);
   
   %savefig(fig,strcat(num2str(i),'.fig'))
end

