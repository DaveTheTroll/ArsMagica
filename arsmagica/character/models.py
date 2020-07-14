from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
import math

class CharacterType(models.Model):
    text = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.text

class VirtueType(models.Model):
    text = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.text

class Virtue(models.Model):
    text = models.CharField(max_length=64, unique=True)
    cost = models.IntegerField()
    virtue_type = models.ForeignKey(VirtueType, on_delete=models.PROTECT)

    def MajorMinor(self):
        if abs(self.cost) == 3: return "Major"
        if abs(self.cost) == 1: return "Minor"
        if abs(self.cost) == 0: return "Free"
        return "[%d]"%self.cost

    def VirtueFlaw(self):
        return "Virtue" if self.cost >= 0 else "Flaw"

    def type(self):
        return self.MajorMinor() + " " + str(self.virtue_type) + " " + self.VirtueFlaw()

    def __str__(self):
        return self.text

class House(models.Model):
    text = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.text

def XPCost(value):
    return int(math.copysign(sum(i for i in range(1, abs(value)+1)), value))

class Characteristic(models.Model):
    text = models.CharField(max_length=20, unique=True)
    abbrev = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.abbrev

class Season:
    def __init__(self, value):
        self.value = value

    seasons = ("Spring", "Summer", "Autumn", "Winter")

    @property
    def year(self):
        return 1200 + int(self.value/4)

    @property
    def season(self):
        return Season.seasons[self.value % 4]

    def __str__(self):
        return "%s %d"%(self.season, self.year)
    
    def __sub__(self, other):
        return (self.value - other.value)/4

class Character(models.Model):
    name = models.CharField(max_length=32, unique=True)
    fullname = models.CharField(max_length=200, unique=True)
    char_type = models.ForeignKey(CharacterType, on_delete=models.PROTECT)
    house = models.ForeignKey(House, null=True, blank=True, on_delete=models.PROTECT)
    birth_season_val = models.IntegerField()
    gauntlet_season_val = models.IntegerField(null=True, blank=True)
    start_season_val = models.IntegerField()
    current_season_val = models.IntegerField()

    @property
    def birth_season(self):
        return Season(self.birth_season_val)

    @property
    def gauntlet_season(self):
        return Season(self.gauntlet_season_val)

    @property
    def start_season(self):
        return Season(self.start_season_val)

    @property
    def current_season(self):
        return Season(self.current_season_val)

    @property
    def age_at_gauntlet(self):
        return int(self.gauntlet_season - self.birth_season)

    @property
    def age_at_start(self):
        return int(self.start_season - self.birth_season)

    @property
    def age(self):
        return int(self.current_season - self.birth_season)

    def clean(self):
        if self.is_magus and self.house == None:
            raise ValidationError("Magus character must have a House")
        if not self.is_magus and self.house != None:
            raise ValidationError("Non-magus character must not have a House")
        if self.is_magus and self.gauntlet_season_val == None:
            raise ValidationError("Magus character must have Gauntlet season")
        if not self.is_magus and self.gauntlet_season_val != None:
            raise ValidationError("Non-magus character must not have Gauntlet season")

    def __str__(self):
        return self.name

    def virtues(self):
        return CharacterVirtue.objects.filter(character=self.pk)

    def characteristics(self):
        return CharacterCharacteristic.objects.filter(character=self.pk)

    def virtue_and_flaw_total(self):
        return sum(v.virtue.cost for v in self.virtues().all())

    def virtue_total(self):
        return sum(v.virtue.cost for v in self.virtues().filter(virtue__cost__gt = 0))

    def flaw_total(self):
        return sum(v.virtue.cost for v in self.virtues().filter(virtue__cost__lt = 0))

    def characteristic_cost(self):
        return sum(c.cost() for c in self.characteristics().all())

    def abilities(self):
        return CharacterAbility.objects.filter(character=self.pk)

    def spent_ability_xp(self):
        return CharacterAbilityXP.objects.filter(ability__character=self.pk).values('source', 'source__text').order_by('source').annotate(xp=models.Sum('xp'))

    def arts(self):
        return CharacterArt.objects.filter(character=self.pk).order_by('art')

    def spent_art_xp(self):
        return CharacterArtXP.objects.filter(art__character=self.pk).values('source', 'source__text').order_by('source').annotate(xp=models.Sum('xp'))

    def spent_xp(self):
        all_xp = {}
        for xp in self.spent_ability_xp():
            all_xp[xp['source__text']] = xp['xp']

        for xp in self.spent_art_xp():
            if xp['source__text'] in all_xp:
                all_xp[xp['source__text']] += xp['xp']
            else:
                all_xp[xp['source__text']] = xp['xp']

        return all_xp

    @property
    def is_magus(self):
        return self.char_type.text == "Magus"

    @property
    def xp_source_available(self):
        xp_source_list = []
        for x in XPSource.objects.all():
            spent = sum(xp.xp for xp in CharacterAbilityXP.objects.filter(ability__character=self.pk, source=x)) + \
                    sum(xp.xp for xp in CharacterArtXP.objects.filter(art__character=self.pk, source=x))
            if x.code == XPSource.EARLY:
                xp_available = 45
            elif x.code == XPSource.NATIVE:
                xp_available = 75
            elif x.code == XPSource.LATER:
                xp_available = (self.age_at_gauntlet-20 if self.is_magus else self.age_at_start-5) * 15
            elif x.code == XPSource.APPRENTICE:
                xp_available = 240 if self.is_magus else 0
            elif x.code == XPSource.AFTER_APPRENTICE:
                xp_available = (self.age_at_start - self.age_at_gauntlet if self.is_magus else 0) * 30
            else:
                xp_available = 0
            
            xp_source_list.append((x.pk, x.text, xp_available, spent))
        return xp_source_list

    def get_absolute_url(self):
        return reverse('sheet', kwargs={'pk': self.pk})   

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
    description = models.CharField(max_length=32)

    class Meta:
        unique_together = (("character", "characteristic"), )

    def __str__(self):
        return str(self.character) + ":" + str(self.characteristic) + ":" + str(self.score)

    def cost(self):
        return XPCost(self.score)

class AbilityType(models.Model):
    text = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.text

class Ability(models.Model):
    text = models.CharField(max_length=32, unique=True)
    abilityType = models.ForeignKey(AbilityType, on_delete=models.PROTECT)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name_plural = "Abilities"

def ScoreFromXP(xp):
    score = 0
    while(xp > score):
        score += 1
        xp -= score
    return score

class CharacterAbility(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    ability = models.ForeignKey(Ability, on_delete=models.PROTECT)
    speciality = models.CharField(max_length=32)

    def xp(self):
        return sum(xp.xp for xp in self.xp_by_source())

    def score(self):
        return ScoreFromXP(self.xp()/5)

    def xp_by_source(self):
        return CharacterAbilityXP.objects.filter(ability=self.pk)

    def xp_by_source_all(self):
        try:
            all_xp = []
            for x in XPSource.objects.all():
                try:
                    this_xp = CharacterAbilityXP.objects.get(ability=self.pk, source=x.pk)
                    all_xp.append([this_xp.pk, x.pk, this_xp.xp])
                except CharacterAbilityXP.DoesNotExist:
                    all_xp.append([-1, x.pk, 0])
            return all_xp
        except Exception as ee:
            print(ee)
        
    class Meta:
        unique_together = (("character", "ability"), )
        verbose_name_plural = "Character abilities"

    def __str__(self):
        return str(self.character) + ":" + str(self.ability)

class XPSource(models.Model):
    text = models.CharField(max_length=20, unique=True)

    # code values
    (GENERAL, EARLY, NATIVE, LATER, APPRENTICE, AFTER_APPRENTICE) = (0,1,2,3,4,5)

    @property
    def code(self):
        if self.text=="Early Childhood":
            return XPSource.EARLY
        elif self.text=="Native Language":
            return XPSource.NATIVE
        elif self.text=="Later Life":
            return XPSource.LATER
        elif self.text=="Apprenticeship":
            return XPSource.APPRENTICE
        elif self.text=="After Apprenticeship":
            return XPSource.AFTER_APPRENTICE
        else:
            return XPSource.GENERAL

    def __str__(self):
        return self.text

class CharacterAbilityXP(models.Model):
    ability = models.ForeignKey(CharacterAbility, on_delete=models.CASCADE)
    source = models.ForeignKey(XPSource, on_delete=models.PROTECT)
    xp = models.IntegerField()

    class Meta:
        unique_together = (("source", "ability"), )

    def __str__(self):
        return str(self.ability) + ":" + str(self.source)

class Art(models.Model):
    text = models.CharField(max_length=20, unique=True)
    abbrev = models.CharField(max_length=3, unique=True)
    form = models.BooleanField()

    def __str__(self):
        return self.text
class CharacterArt(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    art = models.ForeignKey(Art, on_delete=models.PROTECT)

    def xp(self):
        return sum(xp.xp for xp in CharacterArtXP.objects.filter(art=self.pk))

    def score(self):
        return ScoreFromXP(self.xp())

    def xp_by_source_all(self):
        try:
            all_xp = []
            for x in XPSource.objects.all():
                try:
                    this_xp = CharacterArtXP.objects.get(art=self.pk, source=x.pk)
                    all_xp.append([this_xp.pk, x.pk, this_xp.xp])
                except CharacterArtXP.DoesNotExist:
                    all_xp.append([-1, x.pk, 0])
            return all_xp
        except Exception as ee:
            print(ee)

    class Meta:
        unique_together = (("character", "art"), )

    def __str__(self):
        return str(self.character) + ":" + str(self.art)

class CharacterArtXP(models.Model):
    art = models.ForeignKey(CharacterArt, on_delete=models.CASCADE)
    source = models.ForeignKey(XPSource, on_delete=models.PROTECT)
    xp = models.IntegerField()
    class Meta:
        unique_together = (("source", "art"), )

    def __str__(self):
        return str(self.art) + ":" + str(self.source)

class Spell(models.Model):
    name = models.CharField(max_length=64, unique=True)
    technique = models.ForeignKey(Art, on_delete=models.PROTECT, related_name='spell_technique')
    form = models.ForeignKey(Art, on_delete=models.PROTECT, related_name='spell_form')
    requisites = models.ManyToManyField(Art, related_name='spell_requisites')
    level = models.IntegerField()
    notes = models.TextField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name

    def tech_form_level(self):
        tfl = self.technique.abbrev + self.form.abbrev + str(self.level)
        if len(self.requisites) > 0:
            tfl += "("
            for r in self.requisites:
                tfl += r.abbrev
            tfl += ")"
        return tfl

class CharacterSpell(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    spell = models.ForeignKey(Spell, on_delete=models.PROTECT)
    source = models.ForeignKey(XPSource, on_delete=models.PROTECT)

    class Meta:
        unique_together = (("character", "spell"), )

    def __str__(self):
        return str(self.character) +":"+str(self.spell)


    