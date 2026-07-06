from main import main


def test_main_prints_greeting(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello from elgargni-shop!"
