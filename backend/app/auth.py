# from datetime import datetime, timedelta
# from typing import Optional
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from fastapi import HTTPException, status, Depends
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
# from . import models, schemas, config

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# security = HTTPBearer()

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# # def get_password_hash(password):
# #     return pwd_context.hash(password)
# def get_password_hash(password: str) -> str:
#     # Truncate password to 72 bytes to comply with bcrypt limit
#     if len(password.encode('utf-8')) > 72:
#         password = password.encode('utf-8')[:72].decode('utf-8', 'ignore')
#     return pwd_context.hash(password)

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=config.settings.JWT_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, config.settings.JWT_SECRET_KEY, algorithm=config.settings.JWT_ALGORITHM)
#     return encoded_jwt

# def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(credentials.credentials, config.settings.JWT_SECRET_KEY, algorithms=[config.settings.JWT_ALGORITHM])
#         student_id: int = payload.get("sub")
#         if student_id is None:
#             raise credentials_exception
#         return schemas.TokenData(student_id=student_id)
#     except JWTError:
#         raise credentials_exception

# def authenticate_student(db: Session, email: str, password: str):
#     student = db.query(models.Student).filter(models.Student.email == email).first()
#     if not student:
#         return False
#     if not verify_password(password, student.password_hash):
#         return False
#     return student


from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from . import models, schemas, config

# Use bcrypt directly instead of passlib's bcrypt to avoid compatibility issues
import bcrypt

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash"""
    try:
        # Convert string hashed password back to bytes if needed
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    try:
        # Convert to bytes and hash
        password_bytes = password.encode('utf-8')
        
        # Truncate password if it's too long for bcrypt (72 bytes max)
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            print("Warning: Password truncated to 72 bytes for bcrypt")
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string for database storage
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password"
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Ensure 'sub' claim is a string (JWT requirement)
    if 'sub' in to_encode and not isinstance(to_encode['sub'], str):
        to_encode['sub'] = str(to_encode['sub'])
    
    encoded_jwt = jwt.encode(to_encode, config.settings.JWT_SECRET_KEY, algorithm=config.settings.JWT_ALGORITHM)
    return encoded_jwt



def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    print(f"🔐 Token verification started")
    print(f"📨 Received credentials: {credentials.credentials[:20]}...")
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            config.settings.JWT_SECRET_KEY, 
            algorithms=[config.settings.JWT_ALGORITHM]
        )
        student_id_str: str = payload.get("sub")
        print(f"✅ Token decoded successfully. Student ID (string): {student_id_str}")
        print(f"📋 Token payload: {payload}")
        
        if student_id_str is None:
            print("❌ No student ID in token")
            raise credentials_exception
        
        # Convert string student_id back to integer for database use
        try:
            student_id = int(student_id_str)
        except (ValueError, TypeError):
            print("❌ Invalid student ID format in token")
            raise credentials_exception
            
        return schemas.TokenData(student_id=student_id)
        
    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise credentials_exception


def authenticate_student(db: Session, email: str, password: str):
    student = db.query(models.Student).filter(models.Student.email == email).first()
    if not student:
        return False
    if not verify_password(password, student.password_hash):
        return False
    return student