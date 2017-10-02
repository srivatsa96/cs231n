from builtins import range
from builtins import object
import numpy as np

from cs231n.layers import *
from cs231n.layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(self, input_dim=3*32*32, hidden_dim=100, num_classes=10,
                 weight_scale=1e-3, reg=0.0):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - dropout: Scalar between 0 and 1 giving dropout strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian with standard deviation equal to   #
        # weight_scale, and biases should be initialized to zero. All weights and  #
        # biases should be stored in the dictionary self.params, with first layer  #
        # weights and biases using the keys 'W1' and 'b1' and second layer weights #
        # and biases using the keys 'W2' and 'b2'.                                 #
        ############################################################################
        self.params['W1'] = np.random.normal(scale=weight_scale, size=(input_dim,hidden_dim))
        self.params['b1'] = np.zeros((hidden_dim,))
        self.params['W2'] = np.random.normal(scale=weight_scale, size=(hidden_dim,num_classes))
        self.params['b2'] = np.zeros((num_classes,))
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################


    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        layer_1_output, cache1 = affine_forward(X,self.params['W1'],self.params['b1'])
        layer_1_relu, cache1_relu = relu_forward(layer_1_output)
        layer_2_output, cache2 = affine_forward(layer_1_relu, self.params['W2'], self.params['b2'])
        scores = layer_2_output
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grad = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dloss = softmax_loss(scores, y)
        l2 = 0
        ## Adding l2 regularization
        for key,value in self.params.items():
            if(key!='b1' and key!='b2'):
                l2 += np.sum(value * value)

        l2 *= self.reg*0.5

        loss += l2
        ##

        dX2, dW2, db2 = affine_backward(dloss,cache2)
        grad['W2'], grad['b2'] = dW2 + (self.reg)*self.params['W2'], db2
        dZ2 = relu_backward(dX2,cache1_relu)
        dX1, dW1, db1 = affine_backward(dZ2, cache1)
        grad['W1'], grad['b1'] = dW1 + (self.reg)*self.params['W1'] , db1
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grad


class FullyConnectedNet(object):
    """
    A fully-connected neural network with an arbitrary number of hidden layers,
    ReLU nonlinearities, and a softmax loss function. This will also implement
    dropout and batch normalization as options. For a network with L layers,
    the architecture will be

    {affine - [batch norm] - relu - [dropout]} x (L - 1) - affine - softmax

    where batch normalization and dropout are optional, and the {...} block is
    repeated L - 1 times.

    Similar to the TwoLayerNet above, learnable parameters are stored in the
    self.params dictionary and will be learned using the Solver class.
    """

    def __init__(self, hidden_dims, input_dim=3*32*32, num_classes=10,
                 dropout=0, use_batchnorm=False, reg=0.0,
                 weight_scale=1e-2, dtype=np.float32, seed=None):
        """
        Initialize a new FullyConnectedNet.

        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout: Scalar between 0 and 1 giving dropout strength. If dropout=0 then
          the network should not use dropout at all.
        - use_batchnorm: Whether or not the network should use batch normalization.
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
          this datatype. float32 is faster but less accurate, so you should use
          float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers. This
          will make the dropout layers deteriminstic so we can gradient check the
          model.
        """
        self.use_batchnorm = use_batchnorm
        self.use_dropout = dropout > 0
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution with standard deviation equal to  #
        # weight_scale and biases should be initialized to zero.                   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to one and shift      #
        # parameters should be initialized to zero.                                #
        ############################################################################
        input_dimensions= [input_dim] + hidden_dims
        output_dimensions = hidden_dims + [num_classes]
        layer_count = 1;
        for A,B in zip(input_dimensions,output_dimensions):
            self.params['W'+str(layer_count)] = np.random.normal(scale=weight_scale,size=(A,B))
            self.params['b'+str(layer_count)] = np.zeros(shape=(B,))
            if self.use_batchnorm and layer_count != len(input_dimensions):
                self.params['gamma'+str(layer_count)] = np.ones((B,))
                self.params['beta'+str(layer_count)] = np.zeros((B,))
            layer_count+=1
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {'mode': 'train', 'p': dropout}
            if seed is not None:
                self.dropout_param['seed'] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.use_batchnorm:
            self.bn_params = [{'mode': 'train'} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)


    def loss(self, X, y=None):
        """
        Compute loss and gradient for the fully-connected net.

        Input / output: Same as TwoLayerNet above.
        """
        X = X.astype(self.dtype)
        mode = 'test' if y is None else 'train'

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param['mode'] = mode
        if self.use_batchnorm:
            for bn_param in self.bn_params:
                bn_param['mode'] = mode

        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully-connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        activations = [X]
        affineForwardCache = []
        batchnormCache = []
        reluCache = []
        dropoutCache = []

        for layerCount in range(self.num_layers-1):
            ## Affine Forward
            temp_scores,temp_cache = affine_forward(activations[-1],self.params['W'+str(layerCount+1)], self.params['b'+str(layerCount+1)])
            affineForwardCache.append(temp_cache)

            ## Batch normalization Forward
            if self.use_batchnorm:
                temp_scores, temp_cache = batchnorm_forward(temp_scores,self.params['gamma'+str(layerCount+1)], self.params['beta'+str(layerCount+1)], self.bn_params[layerCount])
                batchnormCache.append(temp_cache)

            ## Non Linear Activations Forward
            temp_activation, temp_cache = relu_forward(temp_scores)
            reluCache.append(temp_cache)

            ## Dropout Forward
            if self.use_dropout:
                temp_activation, temp_cache = dropout_forward(temp_activation, self.dropout_param)
                dropoutCache.append(temp_cache)

            activations.append(temp_activation)

        scores,cache = affine_forward(activations[-1],self.params['W'+str(self.num_layers)],self.params['b'+str(self.num_layers)])
        activations.append(scores)
        affineForwardCache.append(cache)

        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early
        if mode == 'test':
            return scores

        loss, grad = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully-connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch normalization, you don't need to regularize the scale   #
        # and shift parameters.                                                    #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        loss, dloss = softmax_loss(scores,y)

        ## Back Pass through output layer
        layerCount = self.num_layers
        dx,dW,db = affine_backward(dloss,affineForwardCache[layerCount-1])
        grad['W'+str(layerCount)] = self.reg*self.params['W'+str(layerCount)] + dW
        grad['b'+str(layerCount)] = db


        layerCount -= 1
        while (layerCount>0):
            ## Dropout Backward
            if self.use_dropout:
                dx = dropout_backward(dx,dropoutCache[layerCount-1])

            ## Back Pass through ReLu layer
            dx = relu_backward(dx,reluCache[layerCount-1])

            ## Back Pass through batchnorm layer
            if self.use_batchnorm:
                dx, dgamma, dbeta = batchnorm_backward(dx, batchnormCache[layerCount-1])
                grad['gamma'+str(layerCount)] = dgamma
                grad['beta'+str(layerCount)] = dbeta

            ## Back pass through Affine layer
            dx,dW,db = affine_backward(dx,affineForwardCache[layerCount-1])
            grad['W'+str(layerCount)] = self.reg*self.params['W'+str(layerCount)] + dW
            grad['b'+str(layerCount)] = db

            layerCount -= 1

        # Apply l2 regularization
        l2 = 0;
        for key,value in self.params.items():
            if(key[0] == 'W'):
                l2 += np.sum(value*value)
        l2*=0.5*self.reg
        loss += l2
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grad