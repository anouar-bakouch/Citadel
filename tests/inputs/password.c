int check_password(int input) {
    int secret = 1234;
    if (input == secret) {
        return 1;
    }
    return 0;
}
