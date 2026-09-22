"""
City Information Modeler.

Layers, and the direction dependencies are allowed to point:

    core/      Stateless data and geometry classes. Depends on nothing in this package
               except other core modules. Every public method is declared parallelizable
               so an external runner can split it.
    parallel/  The external runner. Reads config/compute.yaml, sizes its worker pools from
               the server's cores and RAM, and executes core methods in parallel.
    app/       Orchestration. Imports core classes and composes them in different ways.
    notebooks/ Local testing. Imports from core and app, holds no logic of its own.

core/ never imports from parallel/, app/ or notebooks/.
"""
