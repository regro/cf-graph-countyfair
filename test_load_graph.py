from conda_forge_tick.utils import setup_logging
from conda_forge_tick.make_graph import main as main_make_graph


def test_load_graph_and_update():
    setup_logging(level="DEBUG")
    main_make_graph(
        ctx=None, job=1, n_jobs=1, update_nodes_and_edges=True,
    )
    assert True
