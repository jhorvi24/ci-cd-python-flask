from app import hello_world

def test_hello_world():
    assert hello_world() == "Hello World!"
    print("test_hello_world passed")

