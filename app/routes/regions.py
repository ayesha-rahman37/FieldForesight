from fastapi import APIRouter

router = APIRouter()

ALL_DISTRICTS = [
    # Dhaka Division
    "Dhaka", "Gazipur", "Kishorganj", "Manikganj", "Munshiganj", "Narayanganj", 
    "Narsingdi", "Tangail", "Faridpur", "Gopalganj", "Madaripur", "Rajbari", "Shariatpur",
    
    # Rangpur Division
    "Rangpur", "Dinajpur", "Gaibandha", "Kurigram", "Lalmonirhat", "Nilphamari", 
    "Panchagarh", "Thakurgaon",
    
    # Rajshahi Division
    "Rajshahi", "Bogura", "Joypurhat", "Naogaon", "Natore", "Chapainawabganj", 
    "Pabna", "Sirajganj",
    
    # Chattogram Division
    "Chattogram", "Cox's Bazar", "Bandarban", "Khagrachhari", "Rangamati", "Feni", 
    "Noakhali", "Lakshmipur", "Cumilla", "Brahmanbaria", "Chandpur",
    
    # Khulna Division
    "Khulna", "Bagerhat", "Satkhira", "Jessore", "Jhenaidah", "Magura", 
    "Narail", "Kushtia", "Meherpur", "Chuadanga",
    
    # Barishal Division
    "Barishal", "Barguna", "Bhola", "Jhalokathi", "Patuakhali", "Pirojpur",
    
    # Sylhet Division
    "Sylhet", "Moulvibazar", "Habiganj", "Sunamganj",
    
    # Mymensingh Division
    "Mymensingh", "Jamalpur", "Netrokona", "Sherpur"
]

REGIONS = [{"id": i + 1, "name": district} for i, district in enumerate(ALL_DISTRICTS)]


@router.get("/regions")
def get_regions():
    return REGIONS