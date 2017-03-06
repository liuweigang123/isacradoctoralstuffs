import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime

train_dir = '/home/isaac/Documents/isacradoctoralstuffs/workspace/Tensor_Basics/train'
IMAGE_HIGHT = 1
IMAGE_WIDTH = 10
NUM_CHANNELS = 1
WORK_DIRECTORY = '/home/isaac/Documents/isacradoctoralstuffs/workspace/Tensor_Basics/Data'
BATCH_SIZE = 1

def extract_data(filename, num_images):
    if not tf.gfile.Exists(filename):
        raise ValueError('Failed to find file: ' + filename)
  
    images = np.genfromtxt(filename,delimiter=',',dtype=np.float32)
    images = images.reshape(num_images, IMAGE_HIGHT, IMAGE_WIDTH, NUM_CHANNELS)
    return images

def extract_labels(filename, num_images):
    if not tf.gfile.Exists(filename):
        raise ValueError('Failed to find file: ' + filename)
  
    labels = np.genfromtxt(filename,delimiter=',',dtype=np.float32)

    return labels

def get_file_path(filename):
    filepath = os.path.join(WORK_DIRECTORY, filename)
    return filepath

if tf.gfile.Exists(train_dir):
    tf.gfile.DeleteRecursively(train_dir)
tf.gfile.MakeDirs(train_dir)

train_data_filename = get_file_path('input_seno_data.csv')
train_labels_filename = get_file_path('output_seno_data.csv')

train_data = extract_data(train_data_filename, 90)
train_labels = extract_labels(train_labels_filename, 90)
  
plt.ion()
n_observations = 200

#Placeholders, estruturas do tensorflow onde sao guardados os dados
with tf.name_scope('Inputs'):
    X=tf.placeholder(tf.float32,shape=(BATCH_SIZE, IMAGE_HIGHT, IMAGE_WIDTH, NUM_CHANNELS),name='InputX')
    
    ##################tf.placeholder(tf.float32,name='InputX')
    Y=tf.placeholder(tf.float32, shape=(BATCH_SIZE,),name='InputY')
    ##################tf.placeholder(tf.float32,[90,1,1,1],name='InputY')
Num_Kernels_Con = 15
with tf.name_scope('Weights'):
#weight
    W1 = tf.Variable(tf.random_normal([1,5]),name='Weights')
    W2 = tf.Variable(tf.random_normal([100,1]),name='Weights')
    conv1_weights = tf.Variable(tf.random_normal([1, 2, NUM_CHANNELS, Num_Kernels_Con],
                        stddev=0.1,
                        dtype=np.float32),name='pesosConv1') 
    conv2_weights = tf.Variable(tf.random_normal([1, 2, Num_Kernels_Con, Num_Kernels_Con],
                        stddev=0.1,
                        dtype=np.float32),name='pesosConv1')
    

with tf.name_scope('Biases'):
    #b1 = tf.Variable(tf.random_normal([1,5]),name='Biases')
    b1 = tf.Variable(tf.random_normal([100]),name='Biases')
    b2 = tf.Variable(tf.random_normal([1]),name='Biases')
    bconv = tf.Variable(tf.random_normal([Num_Kernels_Con]),name='Biases')
    bconv2 = tf.Variable(tf.random_normal([Num_Kernels_Con]),name='Biases')
    
#Model-linear regression
def model(data):
    with tf.name_scope('Model'):
        c1 = tf.nn.conv2d(data,
                        conv1_weights,
                        strides=[1, 1, 1, 1],
                        padding='SAME')
        conv1 = tf.add(c1, bconv)
        pool1 = tf.nn.avg_pool(conv1, ksize=[1, 1, 2, 1], strides=[1, 1, 1, 1],
                         padding='SAME', name='pool1')
        c2 = tf.nn.conv2d(pool1,
                        conv2_weights,
                        strides=[1, 1, 1, 1],
                        padding='SAME')
        conv2 = tf.add(c2, bconv2)
        pool2 = tf.nn.avg_pool(conv2, ksize=[1, 1, 2, 1], strides=[1, 1, 1, 1],
                         padding='SAME', name='pool2')
        reshape = tf.reshape(pool2, [BATCH_SIZE, -1])
        dim = reshape.get_shape()[1].value
        W = tf.Variable(tf.truncated_normal(shape=[dim,100],stddev=0.2),name='Weights')
        #W = tf.Variable(tf.truncated_normal(shape=[dim,100]),name='Weights')
        hidden = tf.add(tf.matmul(reshape,W),b1)
        activation = tf.add(tf.matmul(hidden, W2), b2, name='FUllConnected')

    return activation

Y_pred = model(X)

#cost
with tf.name_scope('Loss'):
    #loss = tf.reduce_mean(tf.square(Y_pred - Y))
    loss = tf.reduce_mean(tf.square(Y_pred - train_labels))

#training algorithm
optimizer = tf.train.GradientDescentOptimizer(0.00001)
train = optimizer.minimize(loss)

#initializing the variables
init = tf.global_variables_initializer()

#starting the session session 
sess = tf.Session()
sess.run(init)
cost = tf.scalar_summary("loss",loss)

sess.run(init)
merged_summarry_op = tf.merge_all_summaries()
summary_writer = tf.train.SummaryWriter(train_dir,graph=tf.get_default_graph())
# training the line
epochs = 25000
#Plot
train_size = train_labels.shape[0]
#for step in range(int(epochs * train_size) // BATCH_SIZE):
for step in range(epochs):
    offset = (step * BATCH_SIZE) % (train_size - BATCH_SIZE)
    #offset = (step * BATCH_SIZE) % (train_size) #PEGA TODO O CONJUNTO DE DADOS PARA TREINO
    batch_data = train_data[offset:(offset + BATCH_SIZE), ...]
    batch_labels = train_labels[offset:(offset + BATCH_SIZE)]
    
    feed_dict = {X: batch_data, Y: batch_labels}
    
    _, c, summary=sess.run([train, loss,merged_summarry_op], feed_dict)
    summary_writer.add_summary(summary,step)
  


end = train_data.shape[0]
x_test = train_data[end -BATCH_SIZE:end, ...]
y_test=sess.run(Y_pred,feed_dict = {X:x_test})
y_real = train_labels[end -BATCH_SIZE:end]

out_net = []
out_real = []

fig, ax = plt.subplots(1,1)
ax.grid()
plt.show()

for step in range(train_data.shape[0]// BATCH_SIZE):
    offset = (step * BATCH_SIZE) % (train_size - BATCH_SIZE)
    x_test = train_data[offset:(offset + BATCH_SIZE), ...]
    y_real = train_labels[offset:(offset + BATCH_SIZE)]
    y_test=sess.run(Y_pred,feed_dict = {X:x_test})
    out_net.append(y_test)
    out_real.append(y_real) 
    ax.scatter(y_real,y_test)


basename = "saida.csv"
prefix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
filename = "_".join([prefix,basename])
np.savetxt(filename,(out_net,out_real),delimiter=',')
     
sess.close()