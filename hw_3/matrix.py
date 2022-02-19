import numpy as np
from numpy.lib.mixins import NDArrayOperatorsMixin
import numbers


class Matrix:
    def __init__(self, data):
        if isinstance(data, Matrix):
            self._data = data._data
            self.shape = data.shape
        else:
            if isinstance(data, list) and all(isinstance(x, list) for x in data):
                if not all(all(isinstance(x, (int, float)) for x in row) for row in data):
                    raise ValueError('Expected type: int or float')
                if not all(len(row) == len(data[0]) for row in data):
                    raise ValueError('Rows must have same len')
                self.shape = (len(data), len(data[0]))
                self._data = data
            else:
                raise ValueError('Expected type: list, but got: ', type(data))

    # a + b
    def __add__(self, other):
        if not isinstance(other, Matrix):
            raise ValueError('Expected type: Matrix, but got: ', type(other))
        if self.shape != other.shape:
            raise ValueError('Expected shape: ', self.shape, ', but got: ', other.shape)
        sum = []
        for i in range(self.shape[0]):
            row = []
            for j in range(self.shape[1]):
                row.append(self._data[i][j] + other._data[i][j])
            sum.append(row)
        return Matrix(sum)

    # a * b
    def __mul__(self, other):
        if not isinstance(other, Matrix):
            raise ValueError('Expected type: Matrix, but got: ', type(other))
        if self.shape != other.shape:
            raise ValueError('Expected shape: ', self.shape, ', but got: ', other.shape)
        prod = []
        for i in range(self.shape[0]):
            row = []
            for j in range(self.shape[1]):
                row.append(self._data[i][j] * other._data[i][j])
            prod.append(row)
        return Matrix(prod)

    # a @ b
    def __matmul__(self, other):
        if not isinstance(other, Matrix):
            raise ValueError('Expected type: Matrix, but got: ', type(other))
        if self.shape[1] != other.shape[0]:
            raise ValueError('Expected first dimensions: ', self.shape[1], ', but got: ', other.shape[0])
        prod = []
        for i in range(self.shape[0]):
            row = []
            for j in range(other.shape[1]):
                elem = 0
                for k in range(self.shape[1]):
                    elem += self._data[i][k] * other._data[k][j]
                row.append(elem)
            prod.append(row)
        return Matrix(prod)

    def __repr__(self):
        s = '\n '.join(['[' + ' '.join(map(str, row)) + ']' for row in self._data])
        return '[' + s + ']'


class SaveableMixin():
    def __repr__(self):
        s = '\n '.join(['[' + ' '.join(map(str, row)) + ']' for row in self._value])
        return '[' + s + ']'

    def save(self, filename):
        string_data = self.__repr__()
        with open(filename, 'w') as f:
            f.write(string_data)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class SaveableMatrix(NDArrayOperatorsMixin, SaveableMixin):
    def __init__(self, value):
        self.value = np.asarray(value)

    # One might also consider adding the built-in list type to this
    # list, to support operations like np.add(array_like, list)
    _HANDLED_TYPES = (np.ndarray, numbers.Number, list)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        out = kwargs.get('out', ())
        for x in inputs + out:
            # Only support operations with instances of _HANDLED_TYPES.
            # Use ArrayLike instead of type(self) for isinstance to
            # allow subclasses that don't override __array_ufunc__ to
            # handle ArrayLike objects.
            if not isinstance(x, self._HANDLED_TYPES + (SaveableMatrix,)):
                return NotImplemented

        # Defer to the implementation of the ufunc on unwrapped values.
        inputs = tuple(x.value if isinstance(x, SaveableMatrix) else x
                       for x in inputs)
        if out:
            kwargs['out'] = tuple(
                x.value if isinstance(x, SaveableMatrix) else x
                for x in out)
        result = getattr(ufunc, method)(*inputs, **kwargs)

        if type(result) is tuple:
            # multiple return values
            return tuple(type(self)(x) for x in result)
        elif method == 'at':
            # no return value
            return None
        else:
            # one return value
            return type(self)(result)


class HashMixin:
    """
    В каждой строке считается xor всех чисел, после чего эти значения суммируются.
    """

    def __hash__(self):
        hash = 0
        for i in range(self.shape[0]):
            row_xor = self._data[i][0]
            for j in range(1, self.shape[1]):
                row_xor = row_xor ^ (self._data[i][j])
            hash += row_xor
        return hash


class HashableMatrix(Matrix, HashMixin):
    _hash_table = {}

    # a @ b
    def __matmul__(self, other):
        if not isinstance(other, Matrix):
            raise ValueError('Expected type: Matrix, but got: ', type(other))
        if self.shape[1] != other.shape[0]:
            raise ValueError('Expected first dimensions: ', self.shape[1], ', but got: ', other.shape[0])

        hash_m = (hash(self), hash(other))

        if hash_m not in self._hash_table:
            self._hash_table[hash_m] = HashableMatrix(super(HashableMatrix, self).__matmul__(other))
        return self._hash_table[hash_m]


def main():
    np.random.seed(0)
    a = np.random.randint(0, 10, (10, 10))
    b = np.random.randint(0, 10, (10, 10))
    a_l = a.tolist()
    b_l = b.tolist()

    a_m = Matrix(a_l)
    b_m = Matrix(b_l)
    with open('artifacts/easy/matrix_plus.txt', 'w') as f:
        f.write(str(a_m + b_m))
    with open('artifacts/easy/matrix_mul.txt', 'w') as f:
        f.write(str(a_m * b_m))
    with open('artifacts/easy/matrix_matmul.txt', 'w') as f:
        f.write(str(a_m @ b_m))

    a_m = SaveableMatrix(a_l)
    b_m = SaveableMatrix(b_l)
    (a_m + b_m).save('artifacts/medium/matrix_plus.txt')
    (a_m * b_m).save('artifacts/medium/matrix_mul.txt')
    (a_m @ b_m).save('artifacts/medium/matrix_matmul.txt')

    a = np.random.randint(0, 4, (4, 4))
    b = np.random.randint(0, 4, (4, 4))
    d = b
    c = []
    for i in range(a.shape[0]):
        row = []
        for j in range(a.shape[1]):
            if int(a[i][j]) % 2 == 0:
                row.append(int(a[i][j]) + 1)
            else:
                row.append(int(a[i][j]) - 1)
        c.append(row)
    a_m = HashableMatrix(a.tolist())
    c_m = HashableMatrix(c)
    c = np.array(c)

    if (hash(a_m) == hash(c_m)) and (a != c).any() and (a @ b != c @ d).any():
        b_m = HashableMatrix(b.tolist())
        d_m = HashableMatrix(d.tolist())
        ab = a_m @ b_m
        cd = c @ d
        with open('artifacts/hard/A.txt', 'w') as f:
            f.write(str(a_m))
        with open('artifacts/hard/B.txt', 'w') as f:
            f.write(str(b_m))
        with open('artifacts/hard/C.txt', 'w') as f:
            f.write(str(c_m))
        with open('artifacts/hard/D.txt', 'w') as f:
            f.write(str(d_m))
        with open('artifacts/hard/AB.txt', 'w') as f:
            f.write(str(ab))
        with open('artifacts/hard/CD.txt', 'w') as f:
            f.write(str(HashableMatrix(cd.tolist())))
        with open('artifacts/hard/hash.txt', 'w') as f:
            f.write(f'A @ B: {ab.__hash__()}\n C @ D: {HashableMatrix(cd.tolist()).__hash__()}')
    else:
        print('error')


if __name__ == '__main__':
    main()
