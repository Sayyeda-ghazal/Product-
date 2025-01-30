class PasswordResetRequest(BaseModel):
    email: str
    reset_link: str