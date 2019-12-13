def test_wsgi():
    from donor_reporting_portal.config.wsgi import application
    assert application
