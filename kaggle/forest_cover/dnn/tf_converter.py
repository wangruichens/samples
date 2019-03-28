'''
convert avazu dataset from csv to tfrecord format.
cost about 20 mins.
'''
import tensorflow as tf
import time
import pandas as pd

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed


def _int64_feature(values):
    if not isinstance(values, (tuple, list)):
        values = [values]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=values))


def _bytes_feature(values):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[values]))


def preprocess_line(line,is_train):
    attr = line.strip('\n').split(',')
    if is_train:
        y = attr[-1]
        x=attr[1:-1]
        x=list(map(int, x))
        y=tf.keras.utils.to_categorical(int(y)-1,num_classes=7)
        y = list(map(int, y))
        return x,y
    else:
        x=attr[1:]
        x = list(map(int, x))
        y=tf.keras.utils.to_categorical(int(0),num_classes=7)
        y = list(map(int, y))
        return x,y


@timeit
def csv2tf(path,target,is_train=True):
    # csv=pd.read_csv(path).values
    i = 0
    with tf.python_io.TFRecordWriter(target) as writer:
        with open(path) as f:
            # skip first line
            next(f)
            for line in f:
                i += 1

                x,y = preprocess_line(line,is_train)
                example = tf.train.Example(features=tf.train.Features(feature={
                    # 'continous_feature': _int64_feature(x),
                    'feature': _int64_feature(x),
                    'label': _int64_feature(y)
                }
                ))
                writer.write(example.SerializeToString())
                if i % 10000 == 0:
                    print(i)
                    # break


def main():
    tr_path = '/home/wangrc/data/forest/train.csv'
    csv2tf(tr_path,'train.tfrecord',is_train=True)
    te_path = '/home/wangrc/data/forest/test.csv'
    csv2tf(te_path,'test.tfrecord',is_train=False)


if __name__ == '__main__':
    main()