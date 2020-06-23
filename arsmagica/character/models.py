from django.db import models
import math

class CharacterType(models.Model):
    text = models.CharField(max_length=10)
    
    def __str__(self):
        return self.text

class VirtueType(models.Model):
    text = models.CharField(max_length=20)
    
    def __str__(self):
        return self.text

class Virtue(models.Model):
    text = models.CharField(max_length=64)
    cost = models.IntegerField()
    virtue_type = models.ForeignKey(VirtueType, on_delete=models.PROTECT)

    def __str__(self):
        return self.text

class House(models.Model):
    text = models.CharField(max_length=20)

    def __str__(self):
        return self.text

def XPCost(value):
    return int(math.copysign(sum(i for i in range(1, abs(value)+1)), value))

class Characteristic(models.Model):
    text = models.CharField(max_length=20)
    abbrev = models.CharField(max_length=3)

    def __str__(self):
        return self.abbrev

class Character(models.Model):
    name = models.CharField(max_length=32)
    fullname = models.CharField(max_length=200)
    char_type = models.ForeignKey(CharacterType, null=True, on_delete=models.PROTECT)
    house = models.ForeignKey(House, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def virtues(self):
        return CharacterVirtue.objects.filter(character__pk=self.id)

    def characteristics(self):
        return CharacterCharacteristic.objects.filter(character__pk=self.id)

    def virtue_total(self):
        return sum(v.virtue.cost for v in self.virtues().all())

    def characteristic_cost(self):
        return sum(c.cost() for c in self.characteristics().all())

class CharacterVirtue(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    virtue = models.ForeignKey(Virtue, on_delete=models.PROTECT)
    notes = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self):
        if self.notes:
            return str(self.virtue) + ": " + self.notes
        else:
            return str(self.virtue)

class CharacterCharacteristic(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    characteristic = models.ForeignKey(Characteristic, on_delete=models.PROTECT)
    score = models.IntegerField()

    class Meta:
        unique_together = (("character", "characteristic"), )

    def __str__(self):
        return str(self.character) + ":" + str(self.characteristic) + ":" + str(self.score)

    def cost(self):
        return XPCost(self.score)