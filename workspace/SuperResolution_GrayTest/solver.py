from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
from ops import *
from data import *
from net import *
from utils import *
import os
import time

flags = tf.app.flags
conf = flags.FLAGS
class Solver(object):
  def __init__(self):
    self.device_id = conf.device_id
    self.train_dir = conf.train_dir
    self.samples_dir = conf.samples_dir
    if not os.path.exists(self.train_dir):
      os.makedirs(self.train_dir)
    if not os.path.exists(self.samples_dir):
      os.makedirs(self.samples_dir)    
    #datasets params
    self.num_epoch = conf.num_epoch
    self.batch_size = conf.batch_size
    #optimizer parameter
    self.learning_rate = conf.learning_rate
    if conf.use_gpu:
      device_str = '/gpu:' +  str(self.device_id)
    else:
      device_str = '/cpu:0'
    with tf.device(device_str):
      #dataset
      self.dataset = DataSet(conf.imgs_list_path, conf.lr_imgs_list_path, conf.lr_imgs_test_path ,self.num_epoch, self.batch_size)
      self.net = Net(self.dataset.hr_images, self.dataset.lr_images, 'prsr')
      #optimizer
      self.global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)
      learning_rate = tf.train.exponential_decay(self.learning_rate, self.global_step,
                                           500000, 0.5, staircase=True)
      optimizer = tf.train.RMSPropOptimizer(learning_rate, decay=0.95, momentum=0.9, epsilon=1e-8)
      self.train_op = optimizer.minimize(self.net.loss, global_step=self.global_step)
  def train(self):
    init_op = tf.global_variables_initializer()
    summary_op = tf.summary.merge_all()
    saver = tf.train.Saver()
    # Create a session for running operations in the Graph.
    config = tf.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True
    config.gpu_options.per_process_gpu_memory_fraction = 0.99

    sess = tf.Session(config=config)

    # Initialize the variables (like the epoch counter).
    sess.run(init_op)
    #saver.restore(sess, './models/model.ckpt-30000')
    summary_writer = tf.summary.FileWriter(self.train_dir, sess.graph)
    # Start input enqueue threads.
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)
    iters = 0
    tf.add_to_collection("clogits", self.net.conditioning_logits)
    tf.add_to_collection("plogits",self.net.prior_logits)
    tf.add_to_collection("train",self.net.train)
    tf.add_to_collection("lrimages",self.dataset.lr_images)
    tf.add_to_collection("hrimages",self.dataset.hr_images)
    try:
        while not coord.should_stop():
            # Run training steps or whatever
            t1 = time.time()
            # Estouro da memoria da GPU nesta linha.
            _, loss = sess.run([self.train_op, self.net.loss], feed_dict={self.net.train: True})
            t2 = time.time()
            print('step %d, loss = %.2f (%.1f examples/sec; %.3f sec/batch)' % ((iters, loss, self.batch_size/(t2-t1), (t2-t1))))
            iters += 1
            
            if iters % 10 == 0:
                
                summary_str = sess.run(summary_op, feed_dict={self.net.train: True})
                summary_writer.add_summary(summary_str, iters)
                #self.im_view(sess, mu=1.1, step=iters) #REMOVER DEPOIS
#             if iters % 100 == 0:
#                 checkpoint_path = os.path.join(self.train_dir, 'model.ckpt')
#                 saver.save(sess, checkpoint_path, global_step=iters)
#                 self.sample(sess, mu=1.1, step=iters)
#                 coord.request_stop()
            if iters % 5000 == 0:

                self.sample(sess, mu=1.1, step=iters)
                self.sample_test(sess, mu=1.1, step=iters)

            if iters % 10000 == 0:
                checkpoint_path = os.path.join(self.train_dir, 'model.ckpt')
                saver.save(sess, checkpoint_path, global_step=iters)
                coord.request_stop()
                  
            if iters % 30000 == 0:
                coord.request_stop()  
    except tf.errors.OutOfRangeError:
        print('Done training -- epoch limit reached')
    finally:
        # When done, ask the threads to stop.
        coord.request_stop()

    # Wait for threads to finish.
    coord.join(threads)
    sess.close()
  
  def test(self,sess):
    self.dataset.lr_test_images = self.dataset.getTestData(conf.lr_imgs_test_path)
    self.sample_test(sess, mu=1.1)
  
  def im_view(self, sess, mu=1.1, step=None):
    c_logits = self.net.conditioning_logits
    p_logits = self.net.prior_logits
    lr_imgs = self.dataset.lr_images
    hr_imgs = self.dataset.hr_images
    np_hr_imgs, np_lr_imgs = sess.run([hr_imgs, lr_imgs]) #??????
    
    plt.imshow(np_hr_imgs[0,:,:,0])
    plt.figure()
    plt.imshow(np_lr_imgs[0,:,:,0])
    
  def sample_test(self, sess, mu=1.1, step=None):
    c_logits = self.net.conditioning_logits   
    p_logits = self.net.prior_logits
    lr_imgs = self.dataset.lr_images
    hr_imgs = self.dataset.hr_images       
    #np_lr_imgs = sess.run([lr_imgs])
    #Generate a random matrix of size 32 x 32 of integers values from 0 to 255 (grayscale image) 
    rows = 32
    cols = 32
    num_im = 32
    #random_ims = [[np.matrix(np.random.randint(0,255, size=(rows, cols)))] for k in range(num_im)]
    random_ims = self.dataset.get_corr_white_noise_imgs()
    #for stp in range(3):
    #    np_lr_imgs = np.reshape(random_ims[stp*self.batch_size:(stp*self.batch_size+self.batch_size),:,:],[self.batch_size,rows,cols,1]) #np.reshape(random_ims,[self.batch_size,rows,cols,1])
    np_lr_imgs = np.reshape(random_ims,[self.batch_size,rows,cols,1])
    np_lr_imgs = np.float32(np_lr_imgs)
    gen_hr_imgs = np.zeros((self.batch_size, 32, 32, 1), dtype=np.float32)
    np_c_logits = sess.run(c_logits, feed_dict={lr_imgs:np_lr_imgs, self.net.train:False})
    print('test, iters %d: ' % step)
    for i in range(32):
        for j in range(32):
            for c in range(1):
                np_p_logits = sess.run(p_logits, feed_dict={hr_imgs:gen_hr_imgs})
                new_pixel = logits_2_pixel_value(np_c_logits[:, i, j, c*256:(c+1)*256] + np_p_logits[:, i, j, c*256:(c+1)*256], mu=mu)
                gen_hr_imgs[:, i, j, c] = new_pixel
    save_samples(gen_hr_imgs, self.samples_dir+'/gen_hr_random' + '/generate_' + str(mu*10) + '_' + str(step))
              
  def sample(self, sess, mu=1.1, step=None):
    c_logits = self.net.conditioning_logits
    p_logits = self.net.prior_logits
    lr_imgs = self.dataset.lr_images
    hr_imgs = self.dataset.hr_images
    
    np_hr_imgs, np_lr_imgs = sess.run([hr_imgs, lr_imgs]) #??????
    
    gen_hr_imgs = np.zeros((self.batch_size, 32, 32, 1), dtype=np.float32)
    #gen_hr_imgs = np.zeros((self.batch_size, 32, 32, 3), dtype=np.float32)
    #gen_hr_imgs = np_hr_imgs
    #gen_hr_imgs[:,16:,16:,:] = 0.0
    
    np_c_logits = sess.run(c_logits, feed_dict={lr_imgs: np_lr_imgs, self.net.train:False})
    
    print('iters %d: ' % step)
    
    for i in range(32):
      for j in range(32):
        for c in range(1):
        #for c in range(3):
          np_p_logits = sess.run(p_logits, feed_dict={hr_imgs: gen_hr_imgs})
          new_pixel = logits_2_pixel_value(np_c_logits[:, i, j, c*256:(c+1)*256] + np_p_logits[:, i, j, c*256:(c+1)*256], mu=mu)
          gen_hr_imgs[:, i, j, c] = new_pixel
    #
    save_samples(np_lr_imgs, self.samples_dir +'/lr_imgs'+ '/lr_' + str(mu*10) + '_' + str(step))
    save_samples(np_hr_imgs, self.samples_dir +'/hr_imgs'+ '/hr_' + str(mu*10) + '_' + str(step))
    save_samples(gen_hr_imgs, self.samples_dir+'/gen_hr_imgs' + '/generate_' + str(mu*10) + '_' + str(step))
