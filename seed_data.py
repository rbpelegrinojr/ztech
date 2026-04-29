from models import db, CompanySettings, Category, Product
from urllib.parse import quote_plus


def seed():
    if not CompanySettings.query.first():
        settings = CompanySettings(
            name='ZTech Electronics',
            tagline='Your Microcontroller Parts Supplier',
            address='123 Circuit Street',
            city='Tech City',
            phone='+1-800-ZTECH',
            email='sales@ztech.com',
            website='www.ztech.com',
            currency_symbol='₱',
            tax_rate=12.0
        )
        db.session.add(settings)
        db.session.commit()

    categories = {}
    cat_data = [
        ('Microcontrollers', 'microcontrollers', 'Development boards and microcontroller ICs'),
        ('Sensors', 'sensors', 'Environmental and motion sensors'),
        ('Modules', 'modules', 'Communication and peripheral modules'),
        ('Raspberry Pi', 'raspberry-pi', 'Raspberry Pi boards and accessories'),
    ]
    for name, slug, desc in cat_data:
        cat = Category.query.filter_by(slug=slug).first()
        if not cat:
            cat = Category(name=name, slug=slug, description=desc)
            db.session.add(cat)
    db.session.commit()

    for name, slug, desc in cat_data:
        categories[slug] = Category.query.filter_by(slug=slug).first()

    if Product.query.first():
        return

    def make_image(name):
        return f'https://placehold.co/300x200/1a1a2e/ffffff?text={quote_plus(name)}'

    products = [
        # Microcontrollers
        ('Arduino Uno R3', 'ARD-UNO-R3', 'microcontrollers', 350, 50),
        ('Arduino Mega 2560', 'ARD-MEGA-2560', 'microcontrollers', 650, 30),
        ('Arduino Nano V3', 'ARD-NANO-V3', 'microcontrollers', 180, 100),
        ('Arduino Micro', 'ARD-MICRO', 'microcontrollers', 280, 40),
        ('Arduino Leonardo', 'ARD-LEON', 'microcontrollers', 320, 25),
        ('ESP32 Development Board', 'ESP-32-DEV', 'microcontrollers', 220, 80),
        ('ESP8266 NodeMCU V3', 'ESP-8266-V3', 'microcontrollers', 120, 100),
        ('STM32F103C8T6 Blue Pill', 'STM-32F103', 'microcontrollers', 150, 60),
        ('STM32F401 Black Pill', 'STM-32F401', 'microcontrollers', 280, 40),
        ('ATmega328P DIP', 'ATM-328P', 'microcontrollers', 85, 150),
        ('ATmega2560', 'ATM-2560', 'microcontrollers', 220, 50),
        ('PIC16F877A', 'PIC-16F877A', 'microcontrollers', 95, 80),
        ('PIC18F4550', 'PIC-18F4550', 'microcontrollers', 145, 60),
        ('Teensy 4.0', 'TEEN-4-0', 'microcontrollers', 1200, 20),
        ('RP2040 Pico core', 'RP-2040', 'microcontrollers', 180, 70),
        # Sensors
        ('DHT11 Temperature & Humidity Sensor', 'SEN-DHT11', 'sensors', 45, 200),
        ('DHT22 Temperature & Humidity Sensor', 'SEN-DHT22', 'sensors', 120, 150),
        ('LM35 Temperature Sensor', 'SEN-LM35', 'sensors', 35, 200),
        ('DS18B20 Waterproof Temperature', 'SEN-DS18B20', 'sensors', 85, 100),
        ('BMP180 Barometric Pressure', 'SEN-BMP180', 'sensors', 65, 80),
        ('BMP280 Barometric Pressure', 'SEN-BMP280', 'sensors', 85, 90),
        ('MPU6050 Gyroscope/Accelerometer', 'SEN-MPU6050', 'sensors', 95, 120),
        ('HC-SR04 Ultrasonic Sensor', 'SEN-HCSR04', 'sensors', 55, 150),
        ('PIR Motion Sensor HC-SR501', 'SEN-PIR501', 'sensors', 65, 100),
        ('MQ-2 Gas/Smoke Sensor', 'SEN-MQ2', 'sensors', 75, 80),
        ('MQ-135 Air Quality Sensor', 'SEN-MQ135', 'sensors', 85, 70),
        ('Soil Moisture Sensor', 'SEN-SOIL', 'sensors', 45, 120),
        ('Rain/Water Level Sensor', 'SEN-RAIN', 'sensors', 40, 100),
        ('IR Infrared Obstacle Sensor', 'SEN-IR-OBS', 'sensors', 35, 150),
        ('TCRT5000 Line Tracking Sensor', 'SEN-TCRT5000', 'sensors', 30, 200),
        ('Flex Sensor 2.2"', 'SEN-FLEX22', 'sensors', 280, 30),
        ('Load Cell 5kg with HX711', 'SEN-HX711-5KG', 'sensors', 165, 50),
        # Modules
        ('HC-05 Bluetooth Module', 'MOD-HC05', 'modules', 180, 60),
        ('HC-06 Bluetooth Module', 'MOD-HC06', 'modules', 160, 70),
        ('NRF24L01 2.4GHz Wireless', 'MOD-NRF24L01', 'modules', 95, 100),
        ('SIM800L GSM/GPRS Module', 'MOD-SIM800L', 'modules', 350, 30),
        ('SIM7600 4G LTE Module', 'MOD-SIM7600', 'modules', 1800, 10),
        ('LoRa SX1278 433MHz', 'MOD-LORA-SX1278', 'modules', 320, 25),
        ('L298N Motor Driver', 'MOD-L298N', 'modules', 95, 80),
        ('TB6612FNG Motor Driver', 'MOD-TB6612', 'modules', 85, 60),
        ('L293D Motor Driver IC', 'MOD-L293D', 'modules', 45, 120),
        ('4-Channel Relay Module 5V', 'MOD-RELAY-4CH', 'modules', 120, 70),
        ('8-Channel Relay Module 5V', 'MOD-RELAY-8CH', 'modules', 220, 40),
        ('OLED Display 0.96" I2C', 'MOD-OLED-096', 'modules', 120, 80),
        ('LCD 16x2 with I2C', 'MOD-LCD-162-I2C', 'modules', 95, 100),
        ('TFT LCD 2.4" SPI', 'MOD-TFT-24-SPI', 'modules', 350, 25),
        ('SD Card Module', 'MOD-SD-CARD', 'modules', 55, 150),
        ('RTC DS3231 Module', 'MOD-DS3231', 'modules', 85, 80),
        ('Buck Converter MP1584', 'MOD-BUCK-MP1584', 'modules', 65, 100),
        ('Step-Up Boost Module MT3608', 'MOD-BOOST-MT3608', 'modules', 55, 100),
        # Raspberry Pi
        ('Raspberry Pi 4 Model B 2GB', 'RPI-4B-2GB', 'raspberry-pi', 3200, 15),
        ('Raspberry Pi 4 Model B 4GB', 'RPI-4B-4GB', 'raspberry-pi', 4500, 10),
        ('Raspberry Pi 4 Model B 8GB', 'RPI-4B-8GB', 'raspberry-pi', 6500, 5),
        ('Raspberry Pi 3 Model B+', 'RPI-3BP', 'raspberry-pi', 2800, 8),
        ('Raspberry Pi 3 Model A+', 'RPI-3AP', 'raspberry-pi', 2000, 12),
        ('Raspberry Pi Zero W', 'RPI-ZERO-W', 'raspberry-pi', 850, 20),
        ('Raspberry Pi Zero 2W', 'RPI-ZERO-2W', 'raspberry-pi', 1200, 15),
        ('Raspberry Pi Pico', 'RPI-PICO', 'raspberry-pi', 180, 50),
        ('Raspberry Pi Pico W', 'RPI-PICO-W', 'raspberry-pi', 320, 40),
        ('Raspberry Pi CM4 2GB 8GB Lite', 'RPI-CM4', 'raspberry-pi', 4200, 8),
        ('Official Raspberry Pi Camera v2', 'RPI-CAM-V2', 'raspberry-pi', 1200, 15),
        ('Raspberry Pi Official 7" Touchscreen', 'RPI-TOUCH-7', 'raspberry-pi', 3500, 6),
    ]

    for name, sku, cat_slug, price, stock in products:
        p = Product(
            name=name,
            sku=sku,
            category_id=categories[cat_slug].id,
            price=price,
            stock=stock,
            image_url=make_image(name),
            is_active=True
        )
        db.session.add(p)

    db.session.commit()
