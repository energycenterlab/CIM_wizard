"""
Stateless data and geometry layer.

Every class here holds immutable settings only and every method returns new data, so the
same call in any worker gives the same answer. Public methods declare, through
``contracts.parallelizable``, how an external runner may divide their work. Nothing in this
package reads the compute configuration or starts a worker.
"""
